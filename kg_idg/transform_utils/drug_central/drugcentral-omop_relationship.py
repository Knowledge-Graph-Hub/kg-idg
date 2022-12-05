import uuid

from biolink.model import Association, Disease, Drug, NamedThing  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

'''
This input contains links to a variety of
different concepts, so they need to be
mapped to more specific types based on their
presence in mappings (e.g., if a UMLS CUI
has a mapping to an HP term, the association
will involve the HP term) and their UMLS
semantic type
'''

source_name = "drugcentral-omop_relationship"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()
umls_to_mondo = koza_app.get_map("umls-cui_to_mondo_map")

# Entities
drug = Drug(
    id="DrugCentral:" + row["struct_id"],
    category="biolink:Drug",
)

# TODO: specify association type by relationship_name in table
# TODO: ingest concepts besides diseases
# TODO: add output to merge config

umls_cui = "UMLS:" + row["umls_cui"]

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

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=drug.id,
    predicate="biolink:related_to",
    object=concept.id,
    aggregator_knowledge_source="DrugCentral",
)

koza_app.write(drug, association, concept)
