import uuid

from biolink_model_pydantic.model import ( #type: ignore
    NamedThing,
    Association,
    Predicate
)

from koza.cli_runner import get_koza_app #type: ignore

source_name="atc-classes"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
# Some ATC codes are single letters, to denote top-level parents
# Those will have parents of http://www.w3.org/2002/07/owl#Thing
# There are also some UMLS Semantic Types Ontology (STY) classes in here
# They are ignored because they're only used for UMLS mapping

have_code = False

provider_url = "https://bioportal.bioontology.org/ontologies/ATC"
iri_col_name = "Class ID"
id_only = (row[iri_col_name].split("/"))[-1]

if (row[iri_col_name].split("/"))[-2] != "ATC": 
    # May be STY (UMLS Semantic Types Ontology) or anything else in there
    pass
elif row["ATC LEVEL"] == "1":
    atc_code = NamedThing(id='ATC:' + id_only,
                            iri=row[iri_col_name],
                            name=row["Preferred Label"],
                            provided_by=[provider_url])
    parent_code = NamedThing(id=row["Parents"],
                            iri=row["Parents"],
                            provided_by=[provider_url])
    have_code = True

else:
    atc_code = NamedThing(id='ATC:' + id_only,
                            iri=row[iri_col_name],
                            name=row["Preferred Label"],
                            provided_by=[provider_url])
    parent_code = NamedThing(id='ATC:' + (row["Parents"].split("/"))[-1],
                            iri=row["Parents"],
                            provided_by=[provider_url])
    have_code = True

if have_code:
    # Association
    association = Association(
        id="uuid:" + str(uuid.uuid1()),
        subject=atc_code.id,
        predicate=Predicate.subclass_of,
        object=parent_code.id,
        relation="RO:0002350", #member of
        provided_by=[provider_url]
    )

    koza_app.write(atc_code, association, parent_code)
