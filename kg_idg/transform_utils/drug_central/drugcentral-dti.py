import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Protein,
    Drug,
    DrugToGeneAssociation,
    Predicate,
    Attribute
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-dti"

activity_types = ["A2","AC50","app Ki","app Km","D2"
                    "EC50","EC90","ED50","GI50","IC50",
                    "IC90","ID50","Ka","Kact","Kb","Kd",
                    "Kd1","Ki","Km","Ks","MEC","MIC","MPC",
                    "pA2"]

row = koza_app.get_row(source_name)

# Entities
protein_list = [] # Some drugs have multiple targets provided
for entry in row["ACCESSION"].split("|"):
    protein = Protein(id='UniProtKB:' + entry)
    protein_list.append(protein)

drug = Drug(id='DrugCentral:' + row["STRUCT_ID"])

if row["ACTION_TYPE"]:
    action = ' is ' + (str(row['ACTION_TYPE'])).lower() + ' of '
    full_description = str(row['DRUG_NAME']) + action + str(row['TARGET_CLASS']) + \
                    ' (' + str(row['TARGET_NAME']) + ')'
else:
    full_description = str(row['DRUG_NAME']) + ' targets ' + str(row['TARGET_CLASS']) + \
                    ' (' + str(row['TARGET_NAME']) + ')'

# Association
association = DrugToGeneAssociation( #This works for Gene OR GeneProduct
    id="uuid:" + str(uuid.uuid1()),
    subject=protein.id,
    predicate=Predicate.molecularly_interacts_with,
    object=drug.id,
    relation="RO:0002436", #"molecularly interacts with",
    source = "DrugCentral",
    description=full_description
)

for act_type in activity_types:
    if act_type == str(row['ACT_TYPE']):
        act_attribute = Attribute(
                        name=row['ACT_TYPE'],
                        has_attribute_type="IAO:0000004", # has measurement value
                        has_quantitative_value=row['ACT_VALUE']
                        )
        association.has_attribute = act_attribute
        break

for entry in protein_list:
    koza_app.write(entry, association, drug)
