import uuid

from biolink.model import (  # type: ignore
    Article,
    Book,
    InformationContentEntity,
    InformationResource,
    Publication,
)
from koza.cli_runner import get_koza_app  # type: ignore

# This table is the references only, without Drug IDs.
# see the 'property' table for drug to reference associations.

source_name = "drugcentral-reference"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

if str(row["type"]) == "":
    type_str = "JOURNAL ARTICLE"
else:
    type_str = str(row["type"])

# Entities
if type_str == "JOURNAL ARTICLE":
    if str(row["pmid"]) == "":
        id_str = "DOI:" + row["doi"]
    else:
        id_str = "PMID:" + row["pmid"]
    ice = Article(
        id=id_str,
        type=type_str,
        authors=row["authors"],
        summary=row["title"],
        published_in=row["journal"],
        volume=row["volume"],
        issue=row["issue"],
        creation_date=row["dp_year"],
    )
elif type_str == "BOOK":
    ice = Book(
        id="isbn:" + row["isbn10"],
        type=type_str,
        authors=row["authors"],
        summary=row["title"],
        creation_date=row["dp_year"],
    )
elif type_str in ["CLINICAL TRIAL", "DRUG LABEL"]:
    ice = Publication(
        id=row["url"], type=type_str, summary=row["title"], creation_date=row["dp_year"]
    )
elif type_str == "ONLINE RESOURCE":
    ice = InformationResource(id=row["url"], type=type_str, creation_date=row["dp_year"])
elif type_str == "PATENT":
    patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
    ice = InformationContentEntity(id=patent_id, type=type_str, creation_date=row["dp_year"])
else:
    if (row["document_id"].split(":")) > 1:  # If we have something CURIE-like, use it
        id_str = row["document_id"]
    elif str(row["url"]) != "":  # If not, try a URL
        id_str = row["url"]
    else:
        id_str = "uuid:" + str(uuid.uuid1())  # If not, make a new ID
    ice = InformationContentEntity(
        id=id_str, type=type_str, creation_date=row["dp_year"]
    )

koza_app.write(ice)
