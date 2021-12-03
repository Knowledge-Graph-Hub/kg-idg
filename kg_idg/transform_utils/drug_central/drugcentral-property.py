import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Predicate,
    Drug,
    Publication,
    Article,
    Book,
    InformationResource,
    InformationContentEntity,
    InformationContentEntityToNamedThingAssociation
)

from koza.cli_runner import koza_app #type: ignore

# All literature mentions are treated equivalently at present
# but the property types could be added to drugs
# as attributes (via has_attribute)

# We still need to look up references in the reference table
# though, as we only have table IDs here, not URIs.
# Plus the reference table may include refs not present here.

source_name="drugcentral-property"

row = koza_app.get_row(source_name)
ref_db_id_to_uri = koza_app.get_map('drugcentral-reference_map')

type_str = str(row["reference_type"])
uri = ref_db_id_to_uri[row['db_id']]['uri']

# Entities
if type_str == "JOURNAL ARTICLE":
    ice = Article(id=uri,
                    type=type_str)
elif type_str == "BOOK":
    ice = Book(id=uri,
                type=type_str)
elif type_str in ["CLINICAL TRIAL","DRUG LABEL"]:
    ice = Publication(id=uri,
                        type=type_str)
elif type_str == "ONLINE RESOURCE":
    ice = InformationResource(id=uri,
                            type=type_str)
elif type_str == "PATENT":
    patent_id = "GOOGLE_PATENT:" + str(row["document_id"]).replace(" ", "")
    ice = InformationContentEntity(id=uri,
                                type=type_str)
else:
    ice = InformationContentEntity(id=uri,
                                type=type_str)

drug = Drug(id='DrugCentral:' + row["struct_id"])

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
