#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from shutil import copyfile
from typing import Optional

from kg_idg.transform_utils.transform import Transform

"""
Ingest KGX-format drug - drug target interactions from Drug Central
 and move them to the transformed data folder.
"""

DRUG_CENTRAL_SOURCES = {
    'DrugCentralNodes': 'dc_nodes.tsv',
    'DrugCentralEdges': 'dc_edges.tsv'
}

class DrugCentralTransform(Transform):
    """This transform just ingests the Drug Central transform from KG-COVID-19 and
    copies it to the transform directory.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "drug_central"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(self, nodes_file: Optional[str] = None, edges_file: Optional[str] = None) -> None:  # type: ignore
        """A 'passthrough' transform - all we are doing is just moving the downloaded
        nodes and edges file to the transformed directory.
        Actual moving happens in the parse function, and we call that here.
        """
        if nodes_file and edges_file:
            for source in [nodes_file, edges_file]:
                k = source.split('.')[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in DRUG_CENTRAL_SOURCES.keys():
                name = DRUG_CENTRAL_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)
    
    def parse(self, name: str, data_file: str, source: str) -> None:
        print(f"Copying {data_file}")
        output=os.path.join(self.output_dir, name)
        copyfile(data_file, output)
