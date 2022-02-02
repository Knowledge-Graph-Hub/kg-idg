import uuid

from biolink_model_pydantic.model import ( #type: ignore
    NamedThing,
    Pathway,
    Gene,
    Protein,
    Association
)

from koza.cli_runner import koza_app #type: ignore

source_name="gocams-fix-edges"

def normalize_gocam_id(raw_id,prefix):
    if prefix == "GO":
        thing = NamedThing(id=raw_id)
    elif prefix == "OBO":
        if raw_id[4:13] == "UniProtKB": # edge case
            id = "UniProtKB:" + (raw_id.split("_"))[1]
            thing = Protein(id=id)
        else:
            id = "REACT:" + (raw_id.split("#REACTO_"))[1]
            thing = Pathway(id=id)
    elif prefix == "MGI":
        id = "MGI:" + (raw_id.split(":"))[2]
        thing = Gene(id=id)
    elif prefix == "FB":
        id = "FlyBase:" + (raw_id.split(":"))[1]
        thing = Gene(id=id)
    elif prefix == "WB":
        id = "WormBase:" + (raw_id.split(":"))[1]
        thing = Gene(id=id)
    elif prefix == "POMBASE":
        id = "PomBase:" + (raw_id.split(":"))[2]
        thing = Gene(id=id)                  
    elif prefix == "UniProtKB": 
        thing = Protein(id=raw_id)
    elif prefix in ["DICTYBASE.GENE", "TAIR.LOCUS"]:
        id = raw_id.replace(".","_")
        thing = Gene(id=id)
    elif prefix in ["SGD", "RGD", "XENBASE", "ZFIN"]:
        thing = Gene(id=raw_id)
    else:
        thing = NamedThing(id=raw_id)
    
    return thing

row = koza_app.get_row(source_name)

subject_raw_id = (str(row["subject"])).lstrip(":")
subject_prefix = (subject_raw_id.split(":"))[0]
subject = normalize_gocam_id(subject_raw_id, subject_prefix)

object_raw_id = (str(row["object"])).lstrip(":")
object_prefix = (object_raw_id.split(":"))[0]
object = normalize_gocam_id(object_raw_id, object_prefix)

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=subject.id,
    predicate=row["predicate"],
    object=object.id,
    relation=row["relation"]
)

koza_app.write(subject, association, object)

