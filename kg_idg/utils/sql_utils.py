#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil

import mysql.connector #type: ignore
from mysql.connector import MySQLConnection #type: ignore
import psycopg2 #type: ignore
from psycopg2 import sql #type: ignore
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT #type: ignore
from psycopg2.extensions import connection #type: ignore

def make_temp_mysql_db(username: str, db_name: str) -> MySQLConnection:
    """
    Creates a temporary MySQL database 
    with the provided name.
    Or, if the database already exists,
    removes and re-creates it.
    Returns a MySQL connection object for further operations.
    """

    connection = mysql.connector.connect(
                host="localhost",
                user=username,
                password="pass",
                allow_local_infile=True
                )

    if connection.is_connected():
        db_info = connection.get_server_info()
        print("MySQL server version:", db_info)
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Create temp database if it doesn't exist
        # But if it does, remove it!
        cursor.execute("SHOW DATABASES")
        if (db_name,) in cursor:
            cursor.execute(f"DROP DATABASE {db_name}")
            print(f"Removing old {db_name}.")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Created {db_name}.")

    return connection

def make_temp_postgres_db(username: str, db_name: str) -> connection:
    """
    Creates a temporary PostgreSQL database 
    with the provided name.
    Or, if the database already exists,
    removes and re-creates it.
    Returns a PostgreSQL connection object for further operations.
    """

    system_user = os.environ.get('LOGNAME')

    connection = psycopg2.connect(f"user={username} host=localhost")
    connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    if not connection.closed:
        db_info = connection.server_version
        print("PostgreSQL server version:", db_info)
        cursor = connection.cursor()
        
        # Create temp database if it doesn't exist
        # But if it does, remove it!
        cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(
                        sql.Identifier(db_name)))
        cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                        sql.Identifier(db_name)))

        # Create a role so we don't have to constantly authenticate
        cursor.execute(sql.SQL("DROP ROLE IF EXISTS {}").format(
                        sql.Identifier(system_user)))
        cursor.execute(sql.SQL("CREATE ROLE {} WITH LOGIN SUPERUSER").format(
                        sql.Identifier(system_user)))

        print(f"Created {db_name}.")

    return connection

def process_data_dump(short_name: str, db_type: str, data_file: str, 
                        wanted_tables: list, input_dir: str, output_dir: str, 
                        list_tables: bool) -> bool:
    """
    Given the path to a database dump,
    filters the file by table,
    loads each table, 
    and exports each table as its own TSV.
    This will fail if a server is not running for the 
    necessary database type!
    """

    # TODO: split this into multiple functions

    success = False

    db_name = "temporary_database"

    # Check what type of DB we're working with
    print(f"Database type: {db_type}")
    
    if db_type == "mysql":
        try:

            username = "root"
            connection = make_temp_mysql_db(username, db_name)
            cursor = connection.cursor()

            # List tables in the data dump
            if list_tables:
                print(f"Retrieving table names from {data_file}")
                command = "awk '/INSERT INTO/ && !a[$3]++{print $3}' " + data_file
                os.system(command)

            # Read the specific tables in the data dump
            # We also don't want to load the whole thing
            # Because that takes forever
            output_sql_paths = []
            for table_name in wanted_tables:
                print(f"Reading {table_name} from {data_file}...")
                outfile_sql_path = os.path.join(input_dir, f"{short_name}-{table_name}.sql")
                output_sql_paths.append(outfile_sql_path)
                if not os.path.isfile(outfile_sql_path):
                    command = f"sed -n -e '/DROP TABLE.*`{table_name}`/,/UNLOCK TABLES/p' {data_file} > {outfile_sql_path}"
                    os.system(command)

            # Now load the new, single tables
            # Need to use the mysql interface directly
            # as loading sources isn't supported by the connector
            for outfile_sql_path in output_sql_paths:
                print(f"Loading {outfile_sql_path} into {db_name}...")
                command = f"mysql -u {username} --password=pass {db_name} < {outfile_sql_path}"
                os.system(command)

            # Finally, export tables to TSV
            cursor.execute('USE ' + db_name)
            for table_name in wanted_tables:
                outfile_tsv_path = os.path.join(output_dir, f"{short_name}-{table_name}.tsv")
                print(f"Exporting {table_name} from {db_name} to {outfile_tsv_path}...")
                cursor.execute('SELECT * FROM ' + table_name)
                header = [row[0] for row in cursor.description]
                rows = cursor.fetchall()
                len_rows = str(len(rows))
                with open(outfile_tsv_path, 'w') as outfile:
                    outfile.write('\t'.join(header) + '\n')
                    for row in rows:
                        outfile.write('\t'.join(str(r) for r in row) + '\n')
                print(f"Complete - wrote {len_rows}.")
                
            success = True

        except mysql.connector.errors.DatabaseError as e:
            print(f"Encountered a database error: {e}")
            success = False
    
    elif db_type == "postgres":
        try:

            username = "postgres"
            connection = make_temp_postgres_db(username, db_name)
            cursor = connection.cursor()

            # List tables in the data dump
            if list_tables:
                print(f"Retrieving table names from {data_file}")
                command = "awk '/DROP TABLE IF EXISTS/ && !a[$5]++{print $5}' " + data_file
                os.system(command)

            # Load the data dump - the whole thing,
            # as loading specific tables is challenging with postgresql
            # and the data sets we have in this format are manageable
            print(f"Loading {data_file} into {db_name}...")
            command = f"psql {db_name} < {data_file}"
            os.system(command)

            # Need to re-connect to the database for some reason
            connection = psycopg2.connect(f"user=postgres host=localhost dbname={db_name}")
            connection.autocommit = True
            cursor = connection.cursor()

            # Finally, export specified tables to TSV
            # May need to change the value "public" if schema requires
            delim = '\'\\t\''
            for table_name in wanted_tables:
                # Need full path here, but we write it to a temp directory first
                # Due to some user permission weirdness
                current_path = os.getcwd()
                outfile_tsv_path = os.path.join(current_path, output_dir, f"{short_name}-{table_name}.tsv")
                temp_dir = "/tmp/"
                temp_tsv_path = os.path.join(temp_dir, f"{short_name}-{table_name}.tsv")
                
                print(f"Exporting {table_name} from {db_name} to {outfile_tsv_path}...")
                
                #cursor.execute("SELECT * FROM atc")
                #records = cursor.fetchall()
                #for row in records:
                #    print(row)

                with open(outfile_tsv_path, 'w') as outfile:
                    cursor.copy_expert(("COPY {} TO STDOUT WITH CSV HEADER").format(table_name), 
                                        outfile)
                #print(f"Moving {temp_tsv_path} to {outfile_tsv_path}...")
                #shutil.move(temp_tsv_path, outfile_tsv_path)
            
            print(f"Complete.")
                
            success = True

        except (Exception, psycopg2.Error) as e:
            print(f"Encountered a database error: {e}")
            success = False
    
    else: # Unrecognized database type
        print(f"Did not recognize database type: {db_type}")
        success = False


    return success
