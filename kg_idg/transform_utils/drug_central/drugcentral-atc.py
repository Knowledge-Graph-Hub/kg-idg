import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Drug,
    NamedThing,
    Association,
    Predicate
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-atc"

row = koza_app.get_row(source_name)

# Entities
atc_code = NamedThing(id='ATC:' + row["code"]) # Check for preferred prefix
drug = Drug(id='DrugCentral:' + row["id"])

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=atc_code.id,
    predicate=Predicate.has_part,
    object=drug.id,
    relation="RO:0002351" # "has member"
)

koza_app.write(atc_code, association, drug)
