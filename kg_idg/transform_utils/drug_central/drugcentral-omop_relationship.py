import uuid

from biolink.model import Association, Disease, Drug, NamedThing  # type: ignore
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

relation_to_predicate = {
    "contraindication": "biolink:contraindicated_for",
    "diagnosis": "biolink:diagnoses",
    "indication": "biolink:treats",
    "off-label use": "biolink:treats",
    "reduce risk": "biolink:prevents",
    "symptomatic treatment": "biolink:treats",
}

# Entities
drug = Drug(
    id="DrugCentral:" + row["struct_id"],
    category="biolink:Drug",
)

# TODO: ingest concepts besides diseases
# TODO: add output to merge config

umls_cui = "UMLS:" + row["umls_cui"]
relationship_name = row["relationship_name"]

if umls_cui in umls_to_mondo:
    mondo_id = umls_to_mondo[umls_cui]["mondo_id"]
    concept = Disease(
        id=mondo_id,
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
