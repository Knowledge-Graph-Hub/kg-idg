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

"""Not yet operational."""

"""
Extract and transform Human Protein Atlas contents to node and edge lists.
"""


class DrugCentralTransform(Transform):
    """
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "proteinatlas"
        super().__init__(source_name, input_dir, output_dir)  # set some variables
        self.node_header = ['id', 'name', 'category', 'TDL', 'provided_by']

    def run(self, nodes_file: str, edges_file: str) -> None:  # type: ignore
        """
        """
        self.pass_through(nodes_file=nodes_file, edges_file=edges_file)
