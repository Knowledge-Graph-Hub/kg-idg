#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Optional

from kg_idg.transform_utils.transform import Transform
from koza.cli_runner import transform_source


"""
TCRD is the Target Central Resource Database.
We use this data for the ID mappings necessary to integrate
with Pharos.
See details on source files here:
http://juniper.health.unm.edu/tcrd/download/README
"""

TCRD_SOURCES = {
    'TCRD-IDs': 'TCRDv6.11.0.tsv',
}

TCRD_CONFIGS = {
    'TCRD-IDs': 'tcrd-ids.yaml',
}


TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"

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
            print("Source file not recognized - not transforming.")
        else:
            print(f"Transforming using source in {config}")
            transform_source(source=config, output_dir=output,
                             output_format="tsv",
                             global_table=TRANSLATION_TABLE,
                             local_table=None)
