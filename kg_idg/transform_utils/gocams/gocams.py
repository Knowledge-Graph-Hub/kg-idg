#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from shutil import copyfile
from typing import Optional
from kgx.cli.cli_utils import transform  # type: ignore
from kg_idg.transform_utils.transform import Transform

"""
Ingest GOCAMs from KG-COVID-19.
Moves them to the transformed data directory.
TODO: Use more specific GO-CAMs.
"""

GOCAM_SOURCES = {
    'GOCAMsNodes': 'GOCAMs_nodes.tsv',
    'GOCAMsEdges': 'GOCAMs_edges.tsv'
}

class GOCAMTransform(Transform):
    """This transform ingests the GOCAMs transform from KG-COVID-19 and
    runs a kgx transform for validation.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "gocams"
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
            for k in GOCAM_SOURCES.keys():
                name = GOCAM_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)
    
    def parse(self, name: str, data_file: str, source: str) -> None:
        print(f"Parsing {data_file}")
        transform(inputs=[data_file],
                  input_format='tsv',
                  output=os.path.join(self.output_dir, name),
                  output_format='tsv')
