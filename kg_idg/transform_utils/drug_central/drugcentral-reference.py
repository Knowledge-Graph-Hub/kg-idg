import uuid
from datetime import datetime

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
# Publication types are from MeSH: https://www.nlm.nih.gov/mesh/pubtypes.html

source_name = "drugcentral-reference"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()
ref_name_to_id = koza_app.get_map("drugcentral-jname_to_id_map")

if str(row["type"]) == "":
    type_str = "JOURNAL ARTICLE"
else:
    type_str = str(row["type"])

# Initial check for empty id values
have_id = False
for id_type in ["doi", "document_id", "isbn10", "pmid", "url"]:
    if str(row[id_type]) != "":
        have_id = True
        break
if not have_id:
    print("No valid identifiers found!")

# Entities
try:

    pubdate = datetime.strptime(row["dp_year"], "%Y").date()

    if type_str == "JOURNAL ARTICLE":
        if str(row["pmid"]) == "":
            id_str = "DOI:" + row["doi"]
        else:
            id_str = "PMID:" + row["pmid"]

        # Look up row["journal"]
        # This should be the NLM Catalog abbreviation
        # If there's punctuation, remove before lookup
        pubname = ((row["journal"]).lower()).replace(".", "")
        try:
            pub_id = ref_name_to_id[pubname]["nlm_id"]
        except KeyError:
            pub_id = "NCIT:C17998"  # "Unknown"

        ice = Article(
            id=id_str,
            type=type_str,
            authors=row["authors"],
            summary=row["title"],
            published_in=pub_id,  # Mandatory field
            volume=row["volume"],
            issue=row["issue"],
            creation_date=pubdate,
            category="biolink:Article",
            publication_type="Journal Article"
        )
    elif type_str == "BOOK":
        ice = Book(
            id="isbn:" + row["isbn10"],
            type=type_str,
            authors=row["authors"],
            summary=row["title"],
            creation_date=pubdate,
            category="Book",
            publication_type="Monograph"
        )
    elif type_str in ["CLINICAL TRIAL", "DRUG LABEL"]:
        ice = Publication(
            id=row["url"],
            type=type_str,
            summary=row["title"],
            creation_date=pubdate,
            category="biolink:Publication",
            publication_type="Clinical Study"
        )
    elif type_str == "ONLINE RESOURCE":
        ice = InformationResource(
            id=row["url"],
            type=type_str,
            category="biolink:InformationResource",
            publication_type="Database"
        )
    elif type_str == "PATENT":
        patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
        ice = InformationContentEntity(
            id=patent_id,
            type=type_str,
            creation_date=pubdate,
            category="biolink:InformationContentEntity",
            publication_type="Patent"
        )
    else:
        if (row["document_id"].split(":")) > 1:  # If we have something CURIE-like, use it
            id_str = row["document_id"]
        elif str(row["url"]) != "":  # If not, try a URL
            id_str = row["url"]
        else:
            id_str = "uuid:" + str(uuid.uuid1())  # If not, make a new ID
        ice = InformationContentEntity(
            id=id_str,
            type=type_str,
            creation_date=pubdate,
            category="biolink:InformationContentEntity",
            publication_type="Monograph"
        )

    koza_app.write(ice)

except ValueError as e:
    print(f'Invalid reference: {row["id"]}: {e}')
