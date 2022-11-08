import uuid

from biolink.model import (  # type: ignore
    Association,
    Attribute,
    Drug,
    Protein,
    QuantityValue,
)
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "drugcentral-dti"

activity_types = [
    "A2",
    "AC50",
    "app Ki",
    "app Km",
    "D2",
    "EC50",
    "EC90",
    "ED50",
    "GI50",
    "IC50",
    "IC90",
    "ID50",
    "Ka",
    "Kact",
    "Kb",
    "Kd",
    "Kd1",
    "Ki",
    "Km",
    "Ks",
    "MEC",
    "MIC",
    "MPC",
    "pA2",
]

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
protein_list = []  # Some drugs have multiple targets provided
for entry in row["ACCESSION"].split("|"):
    protein = Protein(id="UniProtKB:" + entry, category="biolink:Protein")
    protein_list.append(protein)

drug = Drug(
    id="DrugCentral:" + row["STRUCT_ID"],
    description=row["DRUG_NAME"],
    category="biolink:Drug",
)

if row["ACTION_TYPE"]:
    action = " is " + (str(row["ACTION_TYPE"])).lower() + " of "
    full_description = (
        str(row["DRUG_NAME"])
        + action
        + str(row["TARGET_CLASS"])
        + " ("
        + str(row["TARGET_NAME"])
        + ")"
    )
else:
    full_description = (
        str(row["DRUG_NAME"])
        + " targets "
        + str(row["TARGET_CLASS"])
        + " ("
        + str(row["TARGET_NAME"])
        + ")"
    )

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=drug.id,
    predicate="biolink:molecularly_interacts_with",
    object=protein.id,
    aggregator_knowledge_source="DrugCentral",
    description=full_description,
)

if str(row["ACT_TYPE"]) in activity_types:
    try:
        quantity = QuantityValue(has_numeric_value=row["ACT_VALUE"], has_unit=row["ACT_TYPE"])
        act_attribute = Attribute(
            id="uuid:" + str(uuid.uuid1()),
            name=row["ACT_TYPE"],
            category="biolink:Attribute",
            has_attribute_type="IAO:0000004",  # has measurement value
            has_quantitative_value=quantity,
        )
        association.has_attribute = act_attribute
    except ValueError:
        print(f'No value found for {row["ACT_TYPE"]} of {row["DRUG_NAME"]} vs {row["TARGET_NAME"]}')
        pass

for entry in protein_list:
    koza_app.write(entry, association, drug)
