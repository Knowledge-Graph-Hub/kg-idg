import uuid

from biolink_model_pydantic.model import Drug #type: ignore

from koza.cli_runner import koza_app #type: ignore

# This parses all DrugCentral cross-references
# Each row is a single xref to a single ID
# so they are all combined upon merge

source_name="drugcentral-identifier"

row = koza_app.get_row(source_name)

xref = []

# the following is a map from id_type to
# preferred prefix
xref_types = {"CHEBI":"CHEBI",
                "ChEMBL_ID":"CHEMBL_COMPOUND",
                "DRUGBANK_ID":"DRUGBANK",
                "INN_ID":"INN",
                "IUPHAR_LIGAND_ID":"IUPHAR_LIGAND",
                "KEGG_DRUG":"KEGG_DRUG",
                "MESH_DESCRIPTOR_UI":"MESH",
                "MESH_SUPPLEMENTAL_RECORD_UI":"MESH",
                "MMSL":"MMSL",
                "NDDF":"NDDF",
                "NDFRT":"NDFRT",
                "NUI":"NUI",
                "PDB_CHEM_ID":"PDB",
                "PUBCHEM_CID":"PUBCHEM_COMPOUND",
                "RXNORM":"RXNORM",
                "SECONDARY_CAS_RN":"CAS",
                "SNOMEDCT_US":"SNOMEDCT",
                "UMLSCUI":"UMLS",
                "UNII":"UNII",
                "VANDF":"VANDF",
                "VUID":"VUID"}
xref.append(xref_types[str(row["id_type"])] + ":" + str(row["identifier"]))

# Entities
drug = Drug(id='DrugCentral:' + row["struct_id"],
            source='DrugCentral',
            xref=xref)

koza_app.write(drug)
