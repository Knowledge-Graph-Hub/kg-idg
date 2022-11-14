import uuid

from biolink.model import (  # type: ignore
    NamedThing
)
from koza.cli_runner import get_koza_app  # type: ignore

# All literature mentions are treated equivalently at present
# but the property types could be added to drugs
# as attributes (via has_attribute)

# We still need to look up references in the reference table
# though, as we only have table IDs here, not URIs.
# Plus the reference table may include refs not present here.

source_name = "drugcentral-omop_relationship"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
# placeholders, filled later from reference table
# if type_str == "JOURNAL ARTICLE":
#     ice = Article(id=uri, type=type_str, published_in="NCIT:C17998", category="biolink:Article")
# elif type_str == "BOOK":
#     ice = Book(id=uri, type=type_str, category="biolink:Book")
# elif type_str in ["CLINICAL TRIAL", "DRUG LABEL"]:
#     ice = Publication(id=uri, type=type_str, category="biolink:Publication")
# elif type_str == "ONLINE RESOURCE":
#     ice = InformationResource(id=uri, type=type_str, category="biolink:InformationResource")
# elif type_str == "PATENT":
#     patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
#     ice = InformationContentEntity(
#         id=uri, type=type_str, category="biolink:InformationContentEntity"
#     )
# else:
#     ice = InformationContentEntity(
#         id=uri, type=type_str, category="biolink:InformationContentEntity"
#     )

# drug = Drug(id="DrugCentral:" + row["struct_id"], category="biolink:Drug")

# # Association
# association = InformationContentEntityToNamedThingAssociation(
#     id="uuid:" + str(uuid.uuid1()),
#     subject=ice.id,
#     predicate="biolink:mentions",
#     object=drug.id,
#     aggregator_knowledge_source="DrugCentral",
# )

# koza_app.write(ice, association, drug)
