import uuid

from biolink.model import Association, NamedThing  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "atc-classes"

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

if (row[iri_col_name].split("/"))[-2] != "UATC":
    # May be STY (UMLS Semantic Types Ontology) or anything else in there
    pass
elif row["ATC LEVEL"] == "1":
    atc_code = NamedThing(
        id="ATC:" + id_only,
        iri=row[iri_col_name],
        name=row["Preferred Label"],
        provided_by=[provider_url],
        category="biolink:NamedThing",
    )
    parent_code = NamedThing(
        id=row["Parents"],
        iri=row["Parents"],
        provided_by=[provider_url],
        category="biolink:NamedThing",
    )
    have_code = True

else:
    atc_code = NamedThing(
        id="ATC:" + id_only,
        iri=row[iri_col_name],
        name=row["Preferred Label"],
        provided_by=[provider_url],
        category="biolink:NamedThing",
    )
    parent_code = NamedThing(
        id="ATC:" + (row["Parents"].split("/"))[-1],
        iri=row["Parents"],
        provided_by=[provider_url],
        category="biolink:NamedThing",
    )
    have_code = True

if have_code:
    # Association
    association = Association(
        id="uuid:" + str(uuid.uuid1()),
        subject=atc_code.id,
        predicate="biolink:subclass_of",
        object=parent_code.id,
    )

    koza_app.write(atc_code, association, parent_code)
