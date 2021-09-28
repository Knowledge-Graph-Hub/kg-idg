#!/usr/bin/env python
# -*- coding: utf-8 -*-
import csv
import gzip
import logging
import os
import re
import tempfile
from collections import defaultdict

from typing import Dict, List, Optional

from kg_idg.transform_utils.transform import Transform
from kg_idg.utils.transform_utils import write_node_edge_item, \
    get_item_by_priority, ItemInDictNotFound, parse_header, data_to_dict, \
    unzip_to_tempdir

""" Not yet operational. """

"""
Reactome provides mappings to pathways in TSVs.
Here, we transform the protein to pathway and CHEBI to pathway mappings
to edge and node lists.
See details on source files here:
https://reactome.org/download-data
"""


class ReactomeTransform(Transform):
    """This transform just ingests the Reactome Protein (UniProt) to 
	pathway and CHEBI to pathway files:
	UniProt2Reactome_PE_Pathway.txt and
	ChEBI2Reactome_PE_Pathway.txt respectively.
	Both are transformed to node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "reactome"
        super().__init__(source_name, input_dir, output_dir) 
        self.node_header = ['id', 'name', 'category', 'TDL', 'provided_by']

    def run(self, nodes_file: str, edges_file: str) -> None:  # type: ignore
        """
        """
        self.pass_through(nodes_file=nodes_file, edges_file=edges_file)
