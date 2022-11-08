import logging
from typing import List

from kg_idg.transform_utils.atc.atc import ATCTransform
from kg_idg.transform_utils.drug_central.drug_central import DrugCentralTransform
from kg_idg.transform_utils.gocams.gocams import GOCAMTransform
from kg_idg.transform_utils.hpa.hpa import ProteinAtlasTransform
from kg_idg.transform_utils.omim.omim import OMIMTransform
from kg_idg.transform_utils.ontology import OntologyTransform
from kg_idg.transform_utils.ontology.ontology_transform import ONTOLOGIES
from kg_idg.transform_utils.orphanet.orphanet import OrphanetTransform
from kg_idg.transform_utils.reactome.reactome import ReactomeTransform
from kg_idg.transform_utils.string.string import STRINGTransform
from kg_idg.transform_utils.tcrd.tcrd import TCRDTransform

DATA_SOURCES = {
    "MondoTransform": OntologyTransform,
    "ChebiTransform": OntologyTransform,
    "HPOTransform": OntologyTransform,
    "GOTransform": OntologyTransform,
    "OGMSTransform": OntologyTransform,
    "DrugCentralTransform": DrugCentralTransform,
    "OrphanetTransform": OrphanetTransform,
    "OMIMTransform": OMIMTransform,
    "ReactomeTransform": ReactomeTransform,
    "GOCAMTransform": GOCAMTransform,
    "TCRDTransform": TCRDTransform,
    "ProteinAtlasTransform": ProteinAtlasTransform,
    "STRINGTransform": STRINGTransform,
    "ATCTransform": ATCTransform,
}


def transform(input_dir: str, output_dir: str, sources: List[str] = None) -> None:
    """Call scripts in kg_idg/transform/[source name]/ to
    transform each source into a graph format that
    KGX can ingest directly, in either TSV or JSON format:
    https://github.com/biolink/kgx/blob/master/data-preparation.md

    Args:
        input_dir: A string pointing to the directory to import data from.
        output_dir: A string pointing to the directory to output data to.
        sources: A list of sources to transform.

    Returns:
        None.

    """
    if not sources:
        # run all sources
        sources = list(DATA_SOURCES.keys())

    for source in sources:
        if source in DATA_SOURCES:
            logging.info(f"Parsing {source}")
            t = DATA_SOURCES[source](input_dir, output_dir)
            if source in ONTOLOGIES.keys():
                t.run(ONTOLOGIES[source])
            else:
                t.run()
