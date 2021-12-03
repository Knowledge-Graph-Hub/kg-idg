import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Publication,
    Drug,
    Predicate,
    InformationContentEntityToNamedThingAssociation
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-reference"

row = koza_app.get_row(source_name)

# Entities
publication = Publication(id='PMID:' + row["pmid"],
                            type=row["type"],
                            authors=row["authors"],
                            summary=row["title"])
drug = Drug(id='DrugCentral:' + row["id"])

# Association
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=publication.id,
    predicate=Predicate.mentions,
    object=drug.id,
    source="DrugCentral",
    relation="IAO:0000142" # "mentions"
)

koza_app.write(publication, association, drug)
