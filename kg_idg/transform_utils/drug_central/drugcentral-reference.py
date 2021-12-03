import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Publication,
    Drug,
    Article,
    Book,
    InformationResource,
    InformationContentEntity,
    Predicate,
    InformationContentEntityToNamedThingAssociation
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-reference"

row = koza_app.get_row(source_name)

if str(row["type"]) == '': 
    type_str = "JOURNAL ARTICLE"
else:
    type_str = str(row["type"])

# Entities
if type_str == "JOURNAL ARTICLE":  #TODO: fix for missing PMIDs - use DOIs?
    if str(row["pmid"]) == '':
        id_str = 'DOI:' + row["doi"]
    else:
        id_str = 'PMID:' + row["pmid"]
    ice = Article(id=id_str,
                    type=type_str,
                    authors=row["authors"],
                    summary=row["title"],
                    published_in=row["journal"],
                    volume=row["volume"],
                    issue=row["issue"],
                    creation_date=row["dp_year"])
elif type_str == "BOOK":
    ice = Book(id='ISBN:' + row["isbn10"],
                            type=type_str,
                            authors=row["authors"],
                            summary=row["title"],
                            creation_date=row["dp_year"])
elif type_str in ["CLINICAL TRIAL","DRUG LABEL"]:
    ice = Publication(id=row["url"],
                            type=type_str,
                            summary=row["title"],
                            creation_date=row["dp_year"])
elif type_str == "ONLINE RESOURCE":
    ice = InformationResource(id=row["url"],
                            type=type_str,
                            creation_date=row["dp_year"])
elif type_str == "PATENT":
    patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
    ice = InformationContentEntity(id=patent_id,
                            type=type_str,
                            creation_date=row["dp_year"])
else:
    ice = InformationContentEntity(id=row["document_id"],
                            type=type_str,
                            creation_date=row["dp_year"])

drug = Drug(id='DrugCentral:' + row["id"])

# Association
association = InformationContentEntityToNamedThingAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=ice.id,
    predicate=Predicate.mentions,
    object=drug.id,
    source="DrugCentral",
    relation="IAO:0000142" # "mentions"
)

koza_app.write(ice, association, drug)
