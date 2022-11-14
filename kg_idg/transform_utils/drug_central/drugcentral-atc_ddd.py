import uuid

from biolink.model import Association, Drug, NamedThing  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

# This is the table for ATC codes and drug dosage definitions
# See https://www.whocc.no/atc_ddd_index/
# DDDs are not currently included

source_name = "drugcentral-atc_ddd"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
atc_code = NamedThing(id="ATC:" + row["atc_code"], category="biolink:NamedThing")
drug = Drug(id="DrugCentral:" + row["struct_id"], category="biolink:Drug")

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=atc_code.id,
    predicate="biolink:related_to_at_concept_level",
    object=drug.id
)

koza_app.write(atc_code, association, drug)
