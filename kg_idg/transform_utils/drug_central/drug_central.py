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

"""
Ingest drug - drug target interactions from Drug Central

Essentially just ingests and transforms this file:
http://unmtid-shinyapps.net/download/drug.target.interaction.tsv.gz

And extracts Drug -> Protein interactions
"""


class DrugCentralTransform(Transform):
    """This transform just ingests the Drug Central transform from KG-COVID-19 and
    copies it to the transform directory
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "drug_central"
        super().__init__(source_name, input_dir, output_dir)  # set some variables
        self.node_header = ['id', 'name', 'category', 'TDL', 'provided_by']

    def run(self, nodes_file: str, edges_file: str) -> None:
        """A 'passthrough' transform - all we are doing is just moving the downloaded
        nodes and edges file to the transformed directory
        """
        self.pass_through(nodes_file=nodes_file, edges_file=edges_file)
