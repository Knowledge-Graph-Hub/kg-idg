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
Ingest gene to disease relationships from Orphanet.
The source document is in n-triple format provided by Monarch.

"""


class OrphanetTransform(Transform):
    """This transform ingests the Orphanet nt file and parses it to KGX tsv format.

    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "orphanet"
        super().__init__(source_name, input_dir, output_dir)  # set some variables
        self.node_header = ['id', 'name', 'category', 'TDL', 'provided_by']

    def run(self, data_file: Optional[str] = None, **kwargs) -> None:  # type: ignore
        """
        Perform the necessary transformations to process Orphanet nt to tsv.
        """
        if not data_file:
            data_file = os.path.join(self.input_base_dir, 'orphanet.nt')

        if 'input_format' in kwargs:
            input_format = kwargs['input_format']
            if input_format not in {'nt', 'ttl', 'rdf/xml'}:
                raise ValueError(f"Unsupported input_format: {input_format}")
        else:
            input_format = 'nt'
        self.parse(data_file, input_format, compression=None)

    def parse(self, data_file: str, input_format: str,
              compression: Optional[str] = None) -> None:
        """
        Processes the Orphanet data file.
        """

        print(f"Parsing {data_file}")
        
        # Define prefix to IRI mappings
        cmap = {
            'ENSEMBL':'http://ensembl.org/id/',
            'GENATLAS':'http://genatlas.medecine.univ-paris5.fr/fiche.php?symbol=',
            'SWISSPROT': 'http://identifiers.org/SwissProt:', # A UniProtAC, really
            'OMIM': 'http://omim.org/entry/', # Can't be sure if this is disease or gene...
            'HGNC': 'https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/',
            'GRAC': 'http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=',
            'ORDO': 'http://www.orpha.net/ORDO/',
            'REACT': 'http://www.reactome.org/PathwayBrowser/#/',
            
        }

        # Define predicates that are to be treated as node properties
        np = {
            'placeholder'
        }

        source: Dict = {
            'input': {
                'format': input_format,
                'compression': compression,
                'filename': data_file,
            },
            'output': {
                'format': 'tsv',
                'compression': None,
                'filename': os.path.join(self.output_dir, self.source_name),
            },
        }
        input_args = prepare_input_args(
            key=self.source_name,
            source=source,
            output_directory=os.path.join(self.output_dir, self.source_name),
            prefix_map=cmap,
            node_property_predicates=np,
            predicate_mappings=None
        )
        output_args = prepare_output_args(
            key=self.source_name,
            source=source,
            output_directory=os.path.join(self.output_dir, self.source_name),
            reverse_prefix_map=None,
            reverse_predicate_mappings=None,
            property_types=None,
        )
        transformer = Transformer(stream=False)
        input_args['filename'] = [input_args['filename']]
        transformer.transform(input_args, output_args)
