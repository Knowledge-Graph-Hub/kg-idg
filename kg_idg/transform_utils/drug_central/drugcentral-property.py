import uuid

from biolink.model import (  # type: ignore
    Article,
    Book,
    Drug,
    InformationContentEntity,
    InformationContentEntityToNamedThingAssociation,
    InformationResource,
    Publication,
)
from koza.cli_runner import get_koza_app  # type: ignore

# All literature mentions are treated equivalently at present
# but the property types could be added to drugs
# as attributes (via has_attribute)

# We still need to look up references in the reference table
# though, as we only have table IDs here, not URIs.
# Plus the reference table may include refs not present here.

# Publication types are from MeSH: https://www.nlm.nih.gov/mesh/pubtypes.html

source_name = "drugcentral-property"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()
ref_db_id_to_uri = koza_app.get_map("drugcentral-reference_map")

type_str = str(row["reference_type"])
uri = ref_db_id_to_uri[row["reference_id"]]["uri"]

# Entities
# placeholders, filled later from reference table
try:
    if type_str == "JOURNAL ARTICLE":
        ice = Article(
            id=uri,
            type=type_str,
            published_in="NCIT:C17998",
            category="biolink:Article",
            publication_type="Journal Article",
        )
    elif type_str == "BOOK":
        ice = Book(id=uri, type=type_str, category="biolink:Book", publication_type="Monograph")
    elif type_str in ["CLINICAL TRIAL", "DRUG LABEL"]:
        ice = Publication(
            id=uri, type=type_str, category="biolink:Publication", publication_type="Clinical Study"
        )
    elif type_str == "ONLINE RESOURCE":
        ice = InformationResource(
            id=uri,
            type=type_str,
            category="biolink:InformationResource",
            publication_type="Database",
        )
    elif type_str == "PATENT":
        patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
        ice = InformationContentEntity(
            id=uri,
            type=type_str,
            category="biolink:InformationContentEntity",
            publication_type="Patent",
        )
    else:
        ice = InformationContentEntity(
            id=uri,
            type=type_str,
            category="biolink:InformationContentEntity",
            publication_type="Monograph",
        )

    drug = Drug(id="DrugCentral:" + row["struct_id"], category="biolink:Drug")

    # Association
    association = InformationContentEntityToNamedThingAssociation(
        id="uuid:" + str(uuid.uuid1()),
        subject=ice.id,
        predicate="biolink:mentions",
        object=drug.id,
        aggregator_knowledge_source="DrugCentral",
    )

    koza_app.write(ice, association, drug)

except ValueError as e:
    print(f'Invalid reference in property: {row["id"]}: {e}')
