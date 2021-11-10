import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Protein,
    Drug,
    Association,
    Predicate,
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-dti"

row = koza_app.get_row(source_name)

# Entities
protein_list = [] # Some drugs have multiple targets provided
for entry in row["ACCESSION"].split("|"):
    protein = Protein(id='UniProtKB:' + entry)
    protein_list.append(protein)

drug = Drug(id='DrugCentral:' + row["STRUCT_ID"])

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=protein.id,
    predicate=Predicate.molecularly_interacts_with,
    object=drug.id,
    relation="RO:0002436" #"molecularly interacts with"
)

for entry in protein_list:
    koza_app.write(entry, association, drug)
