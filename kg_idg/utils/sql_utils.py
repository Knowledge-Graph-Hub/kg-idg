#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import mysql.connector #type: ignore
from mysql.connector import MySQLConnection #type: ignore

def make_temp_db(username: str, db_name: str) -> MySQLConnection:
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
        cursor = connection.cursor()
        
        # Create temp database if it doesn't exist
        # But if it does, remove it!
        cursor.execute("SHOW DATABASES")
        if (db_name,) in cursor:
            cursor.execute(f"DROP DATABASE {db_name}")
            print(f"Removing old {db_name} database.")
        cursor.execute(f"CREATE DATABASE {db_name}")
        print(f"Created {db_name} database.")

    return connection

def process_data_dump(data_file: str, wanted_tables: list, input_dir: str,
                        output_dir: str, list_tables: bool) -> bool:
    """
    Given the path to a TCRD MySQL data dump,
    loads the file with sqlparse,
    and exports each table as its own TSV.
    This will fail if a mysql server is not running!
    """

    success = False

    username = "root"
    db_name = "tcrd"

    try:

        connection = make_temp_db(username, db_name)
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
            outfile_sql_path = os.path.join(input_dir, f"tcrd-{table_name}.sql")
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
            outfile_tsv_path = os.path.join(output_dir, f"tcrd-{table_name}.tsv")
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
    
    return success
