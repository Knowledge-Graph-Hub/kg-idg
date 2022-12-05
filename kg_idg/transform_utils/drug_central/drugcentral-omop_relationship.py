import uuid

from biolink.model import (  # type: ignore
    Association,
    Disease,
    Drug,
    NamedThing,
    PhenotypicFeature,
)
from koza.cli_runner import get_koza_app  # type: ignore

"""
This input contains links to a variety of
different concepts, so they need to be
mapped to more specific types based on their
presence in mappings (e.g., if a UMLS CUI
has a mapping to an HP term, the association
will involve the HP term) and their UMLS
semantic type
"""

source_name = "drugcentral-omop_relationship"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()
umls_to_mondo = koza_app.get_map("umls-cui_to_mondo_map")
umls_to_hp = koza_app.get_map("umls-cui_to_hp_map")

relation_to_predicate = {
    "contraindication": "biolink:contraindicated_for",
    "diagnosis": "biolink:diagnoses",
    "indication": "biolink:treats",
    "off-label use": "biolink:treats",
    "reduce risk": "biolink:prevents",
    "symptomatic treatment": "biolink:treats",
}

sty_disease_terms = ["STY:T020",
                     "STY:T033",
                     "STY:T047",
                     "STY:T048",
                     "STY:T049",
                     "STY:T191",
                     ]

# Check if there's a UMLS CUI to begin with
while len(row["umls_cui"].strip()) == 0:
    row = koza_app.get_row()

# Entities
drug = Drug(
    id="DrugCentral:" + row["struct_id"],
    category="biolink:Drug",
)

# TODO: add output to merge config
# TODO: include proper category for UMLS CUI
# if not categorized; use STY type

umls_cui = "UMLS:" + row["umls_cui"]
relationship_name = row["relationship_name"]

if umls_cui in umls_to_mondo:
    mondo_id = umls_to_mondo[umls_cui]["mondo_id"]
    concept = Disease(
        id=mondo_id,
        category="biolink:Disease",
    )
elif umls_cui in umls_to_hp:
    hp_id = umls_to_hp[umls_cui]["hp_id"]
    concept = PhenotypicFeature(
        id=hp_id,
        category="biolink:PhenotypicFeature",
    )
else:
    if row["cui_semantic_type"] in sty_disease_terms:
        concept = Disease(
            id=umls_cui,
            category="biolink:Disease",
        )
    else:
        concept = NamedThing(
            id=umls_cui,
            category="biolink:NamedThing",
        )

predicate = relation_to_predicate[relationship_name]

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=drug.id,
    predicate=predicate,
    object=concept.id,
    aggregator_knowledge_source="DrugCentral",
)

koza_app.write(drug, association, concept)
