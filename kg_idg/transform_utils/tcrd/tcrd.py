#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Optional

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
        else:
            if name[-3:] == "tsv": #This is just the ID map
                print(f"Transforming using source in {config}")
                transform_source(source=config, output_dir=output,
                             output_format="tsv",
                             global_table=TRANSLATION_TABLE,
                             local_table=None)
            elif name[-3:] == "sql": 
                #This is the full SQL dump
                # So we need to convert it to TSV first,
                # then pass to Koza transform_source
                print("Transforming MySQL dump to TSV...")

