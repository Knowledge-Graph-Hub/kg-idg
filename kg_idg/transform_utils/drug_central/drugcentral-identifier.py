import uuid

from biolink.model import Association, Drug, NamedThing  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

# This parses all DrugCentral cross-references
# Each row could be a single xref to a single ID
# but that isn't supported by BioLink yet
# so we have a workaround with Association

source_name = "drugcentral-identifier"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# the following is a map from id_type to
# preferred prefix
xref_types = {
    "CHEBI": "CHEBI",
    "ChEMBL_ID": "CHEMBL_COMPOUND",
    "DRUGBANK_ID": "DRUGBANK",
    "INN_ID": "INN",
    "IUPHAR_LIGAND_ID": "IUPHAR_LIGAND",
    "KEGG_DRUG": "KEGG_DRUG",
    "MESH_DESCRIPTOR_UI": "MESH",
    "MESH_SUPPLEMENTAL_RECORD_UI": "MESH",
    "MMSL": "MMSL",
    "NDDF": "NDDF",
    "NUI": "NDFRT",
    "PDB_CHEM_ID": "PDB",
    "PUBCHEM_CID": "PUBCHEM_COMPOUND",
    "RXNORM": "RXNORM",
    "SECONDARY_CAS_RN": "CAS",
    "SNOMEDCT_US": "SNOMEDCT",
    "UMLSCUI": "UMLS",
    "UNII": "UNII",
    "VANDF": "VANDF",
    "VUID": "VUID",
}

# Entities
# CHEBI IDs already prefixed for some reason
if str(row["id_type"]) == "CHEBI":
    xref_curie = NamedThing(id=str(row["identifier"]), category="biolink:NamedThing")
else:
    xref_curie = NamedThing(
        id=xref_types[str(row["id_type"])] + ":" + str(row["identifier"]),
        category="biolink:NamedThing",
    )
drug = Drug(id="DrugCentral:" + row["struct_id"], category="biolink:Drug")

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=xref_curie.id,
    predicate="biolink:same_as",
    object=drug.id,
    aggregator_knowledge_source="DrugCentral",
)

koza_app.write(xref_curie, association, drug)
