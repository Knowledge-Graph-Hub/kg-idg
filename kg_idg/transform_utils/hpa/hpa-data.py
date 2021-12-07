import uuid

from biolink_model_pydantic.model import Protein #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="hpa-data"

row = koza_app.get_row(source_name)

# Entities
protein_list = [] # Some entries have multiple protein IDs
xref_list = []

xref_types = {"ENSEMBL:":'Ensembl'}
for xref_type in xref_types:
    value = row[xref_types[xref_type]]
    value = value.replace("/","_") #Gotta handle illegal slashes
    if str(value) == 'None':
        continue
    else:
        xref_list.append(xref_type + str(value))

for entry in row["Uniprot"].split(", "):
    if entry != "":
        protein = Protein(id='UniProtKB:' + entry,
                    source="Human Protein Atlas",
                    xref=xref_list)
        protein_list.append(protein)

for entry in protein_list:
    koza_app.write(protein)
