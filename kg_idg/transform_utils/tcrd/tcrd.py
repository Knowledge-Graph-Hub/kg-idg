#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Optional
import subprocess

import mysql.connector

from kg_idg.transform_utils.transform import Transform
from koza.cli_runner import transform_source #type: ignore


"""
TCRD is the Target Central Resource Database.
We use this data for the ID mappings necessary to integrate
with Pharos.
We also download the full MySQL dump and convert it to TSV
(rather than trying to re-load the whole DB).
See details on source files here:
http://juniper.health.unm.edu/tcrd/download/README
"""

TCRD_SOURCES = {
    'TCRD-IDs': 'TCRDv6.12.4.tsv',
    'TCRD-DB': 'tcrd.sql'
}

TCRD_CONFIGS = {
    'TCRD-IDs': 'tcrd-ids.yaml',
    'TCRD-DB': 'tcrd-db.yaml',
}

WANTED_TABLES = ["data_type","info_type","protein","target","tdl_info"]

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"

class SplitterArgs:
    # Setup for the MySQL parser
    def __init__(self): pass

class TCRDTransform(Transform):
    """This transform ingests the tab-delimited TCRD ID mapping file.
	It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "tcrd"
        super().__init__(source_name, input_dir, output_dir) 

    def run(self, tcrd_id_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the TCRD ID file for Koza and call the parse function.
        """
        if tcrd_id_file:
            for source in [tcrd_id_file]:
                k = source.split('.')[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in TCRD_SOURCES.keys():
                name = TCRD_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def process_tcrd_data_dump(self, data_file: str) -> None:
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
            connection = mysql.connector.connect(
                    host="localhost",
                    user=username,
                    password="pass",
                    allow_local_infile=True
                    )
            if connection.is_connected():
                db_Info = connection.get_server_info()
                print("MySQL server version:", db_Info)
                cursor = connection.cursor()
                
                # Create temp database if it doesn't exist
                # But if it does, remove it!
                cursor.execute("SHOW DATABASES")
                if (db_name,) in cursor:
                    cursor.execute(f"DROP DATABASE {db_name}")
                    print(f"Removing old {db_name} database.")
                cursor.execute(f"CREATE DATABASE {db_name}")
                print(f"Created {db_name} database.")
                    
                # List tables in the data dump
                print(f"Retrieving table names from {data_file}")
                command = "awk '/INSERT INTO/ && !a[$3]++{print $3}' " + data_file
                os.system(command)

                # Read the specific tables in the data dump
                # We also don't want to load the whole thing
                # Because that takes forever
                output_sql_paths = []
                for table_name in WANTED_TABLES:
                    print(f"Reading {table_name} from {data_file}...")
                    outfile_sql_path = os.path.join(self.input_base_dir, f"tcrd-{table_name}.sql")
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
                for table_name in WANTED_TABLES:
                    outfile_tsv_path = os.path.join(self.output_dir, f"tcrd-{table_name}.tsv")
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

            connection.close()

        except mysql.connector.errors.DatabaseError as e:
            print(f"Encountered a database error: {e}")
            success = False
        
        return success

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform TCRD ID mapping file with Koza.
        """
        print(f"Parsing {data_file}")
        config = os.path.join("kg_idg/transform_utils/tcrd/", TCRD_CONFIGS[source])
        output = self.output_dir

        # If source is unknown then we aren't going to guess
        if source not in TCRD_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")

        if name[-3:] == "sql": 
                '''
                This is the full SQL dump so we need to load it as a local database,
                export it as individual TSVs,
                then pass what we want to Koza transform_source.
                '''
                print("Transforming MySQL dump to TSV. This may take a while...")
                if not self.process_tcrd_data_dump(data_file):
                    print("Did not process TCRD mysql dump!")
                    return

        print(f"Transforming using source in {config}")
        transform_source(source=config, output_dir=output,
                             output_format="tsv",
                             global_table=TRANSLATION_TABLE,
                             local_table=None)

