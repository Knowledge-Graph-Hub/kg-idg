import uuid

from biolink.model import (  # type: ignore
    Association,
    Gene,
    NamedThing,
    Pathway,
    Protein,
)
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "gocams-fix-edges"


def normalize_gocam_id(raw_id, prefix):
    if prefix == "OBO":
        if raw_id[4:13] == "UniProtKB":  # edge case
            curie = "UniProtKB:" + (raw_id.split("_"))[1]
            thing = Protein(id=curie, category="biolink:Protein")
        else:
            curie = "REACT:" + (raw_id.split("#REACTO_"))[1]
            thing = Pathway(id=curie, category="biolink:Pathway")
    elif prefix == "MGI":
        curie = "MGI:" + (raw_id.split(":"))[2]
        thing = Gene(id=curie, category="biolink:Gene")
    elif prefix == "FB":
        curie = "FlyBase:" + (raw_id.split(":"))[1]
        thing = Gene(id=curie, category="biolink:Gene")
    elif prefix == "WB":
        curie = "WormBase:" + (raw_id.split(":"))[1]
        thing = Gene(id=curie, category="biolink:Gene")
    elif prefix == "POMBASE":
        curie = "PomBase:" + (raw_id.split(":"))[2]
        thing = Gene(id=curie, category="biolink:Gene")
    elif prefix == "UniProtKB":
        thing = Protein(id=raw_id, category="biolink:Protein")
    elif prefix in ["DICTYBASE.GENE", "TAIR.LOCUS"]:
        curie = raw_id.replace(".", "_")
        thing = Gene(id=curie, category="biolink:Gene")
    elif prefix in ["SGD", "RGD", "XENBASE", "ZFIN"]:
        thing = Gene(id=raw_id, category="biolink:Gene")
    else:
        thing = NamedThing(id=raw_id, category="biolink:NamedThing")

    return thing


koza_app = get_koza_app(source_name)
row = koza_app.get_row()

subject_raw_id = (str(row["subject"])).lstrip(":")
subject_prefix = (subject_raw_id.split(":"))[0]
subject = normalize_gocam_id(subject_raw_id, subject_prefix)

object_raw_id = (str(row["object"])).lstrip(":")
object_prefix = (object_raw_id.split(":"))[0]
object = normalize_gocam_id(object_raw_id, object_prefix)

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()), subject=subject.id, predicate=row["predicate"], object=object.id
)

koza_app.write(subject, association, object)
