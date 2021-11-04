#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from typing import Optional
from kgx.cli.cli_utils import transform  # type: ignore
from kg_idg.transform_utils.transform import Transform

"""
Ingest KGX-format human protein-protein interactions from
STRING and move them to the transformed data folder.
"""

STRING_SOURCES = {
    'STRINGNodes': 'string_nodes.tsv',
    'STRINGEdges': 'string_edges.tsv'
}

class STRINGTransform(Transform):
    """Ingests the STRING human subset transform from KG-COVID-19 and
    runs a kgx transform for validation.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "string"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(self, nodes_file: Optional[str] = None, edges_file: Optional[str] = None) -> None:  # type: ignore
        """A 'passthrough' transform with a kgx transform in the middle.
        Actual moving happens in the parse function, and we call that here.
        """
        if nodes_file and edges_file:
            for source in [nodes_file, edges_file]:
                k = source.split('.')[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in STRING_SOURCES.keys():
                name = STRING_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)
    
    def parse(self, name: str, data_file: str, source: str) -> None:
        print(f"Parsing {data_file}")
        transform(inputs=[data_file],
                  input_format='tsv',
                  output=os.path.join(self.output_dir, name),
                  output_format='tsv')
