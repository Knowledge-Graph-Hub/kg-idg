#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Optional
import gzip
import shutil

from kg_idg.transform_utils.transform import Transform
from kg_idg.utils.sql_utils import process_data_dump
from koza.cli_runner import transform_source #type: ignore

"""
DrugCentral provides a set of drug vs. target interactions.
We integrate this data with TRCD contents.
See all available files here:
https://unmtid-shinyapps.net/download/DrugCentral/
"""

DRUG_CENTRAL_SOURCES = {
    'DrugCentralDTI': 'drug.target.interaction.tsv.gz',
    'DrugCentralDB': 'drugcentral.dump.010_05_2021.sql.gz'
}

DRUG_CENTRAL_CONFIGS = {
    'DrugCentralDTI': 'drugcentral-dti.yaml',
    'DrugCentralDB': 'drugcentral-{table}.yaml'
}

WANTED_TABLES = ["atc_ddd","approval","reference"]

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"

class DrugCentralTransform(Transform):
    """This transform ingests the tab-delimited DrugCentral
    drug-target interactions file.
	It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "drug_central"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(self, dc_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the DrugCentral file for Koza and call the parse function.
        """
        if dc_file:
            for source in [dc_file]:
                k = source.split('.')[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in DRUG_CENTRAL_SOURCES.keys():
                name = DRUG_CENTRAL_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)
    
    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform DrugCentral file with Koza.
        Need to decompress it first.
        """
        print(f"Parsing {data_file}")

        # Decompress
        outname = name[:-3]
        outpath = os.path.join(self.input_base_dir, outname)
        with gzip.open(data_file, 'rb') as data_file_gz:
            with open(outpath, 'wb') as data_file_new:
                shutil.copyfileobj(data_file_gz, data_file_new)

        # If source is unknown then we aren't going to guess
        if source not in DRUG_CENTRAL_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")

        if outname[-3:] == "sql": 
            '''
            This is the full SQL dump so we need to load it as a local database,
            export it as individual TSVs,
            then pass what we want to Koza transform_source.
            '''
            print("Transforming data dump to TSV. This may take a while...")
            if not process_data_dump("drugcentral",
                                    "postgres",
                                    outpath, 
                                    WANTED_TABLES, 
                                    self.input_base_dir,
                                    self.output_dir,
                                    list_tables=False):
                print("Did not process DrugCentral data dump!")
                return
        
        output = self.output_dir
        if source == "DrugCentralDB": # Configs vary by DB table
            for table in WANTED_TABLES:
                config = os.path.join("kg_idg/transform_utils/drug_central/", f'drugcentral-{table}.yaml')
                print(f"Transforming to {output} using source in {config}")
                transform_source(source=config, output_dir=output,
                                output_format="tsv",
                                global_table=TRANSLATION_TABLE,
                                local_table=None)
        else:
            config = os.path.join("kg_idg/transform_utils/drug_central/", DRUG_CENTRAL_CONFIGS[source])
            print(f"Transforming to {output} using source in {config}")
            transform_source(source=config, output_dir=output,
                             output_format="tsv",
                             global_table=TRANSLATION_TABLE,
                             local_table=None)


