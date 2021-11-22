import uuid

from biolink_model_pydantic.model import ( #type: ignore
    NamedThing,
    Association,
    Predicate
)

from koza.cli_runner import koza_app #type: ignore

source_name="atc-classes"

row = koza_app.get_row(source_name)

# Entities
# Some ATC codes are single letters, to denote top-level parents
# Those will have parents of http://www.w3.org/2002/07/owl#Thing
# There are also some UMLS Semantic Types Ontology (STY) classes in here
# They are ignored because they're only used for UMLS mapping

have_code = False

if row["ATC LEVEL"] == "1":
    atc_code = NamedThing(id='ATC:' + (row["Class ID"].split("/"))[-1],
                            iri=row["Class ID"],
                            name=row["Preferred Label"],
                            provided_by=["https://bioportal.bioontology.org/ontologies/ATC"])
    parent_code = NamedThing(id=row["Parents"],
                            iri=row["Parents"],
                            provided_by=["https://bioportal.bioontology.org/ontologies/ATC"])
    have_code = True
elif (row["Class ID"].split("/"))[-2] == "STY": # UMLS Semantic Types Ontology
    pass
else:
    atc_code = NamedThing(id='ATC:' + (row["Class ID"].split("/"))[-1],
                            iri=row["Class ID"],
                            name=row["Preferred Label"],
                            provided_by=["https://bioportal.bioontology.org/ontologies/ATC"])
    parent_code = NamedThing(id='ATC:' + (row["Parents"].split("/"))[-1],
                            iri=row["Parents"],
                            provided_by=["https://bioportal.bioontology.org/ontologies/ATC"])
    have_code = True

if have_code:
    # Association
    association = Association(
        id="uuid:" + str(uuid.uuid1()),
        subject=atc_code.id,
        predicate=Predicate.subclass_of,
        object=parent_code.id,
        relation="RO:0002350", #member of
        provided_by=["https://bioportal.bioontology.org/ontologies/ATC"]
    )

    koza_app.write(atc_code, association, parent_code)
