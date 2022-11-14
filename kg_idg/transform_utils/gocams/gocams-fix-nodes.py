from biolink.model import Gene, NamedThing, Pathway, Protein  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "gocams-fix-nodes"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

raw_id = (str(row["id"])).lstrip(":")
prefix = (raw_id.split(":"))[0]

if prefix == "OBO":
    if raw_id[4:13] == "UniProtKB":  # edge case
        id = "UniProtKB:" + (raw_id.split("_"))[1]
        thing = Protein(id=id, provided_by=row["provided_by"], category="biolink:Protein")
    else:
        id = "REACT:" + (raw_id.split("#REACTO_"))[1]
        thing = Pathway(id=id, provided_by=row["provided_by"], category="biolink:Pathway")
elif prefix == "MGI":
    id = "MGI:" + (raw_id.split(":"))[2]
    thing = Gene(id=id, provided_by=row["provided_by"], category="biolink:Gene")
elif prefix == "FB":
    id = "FlyBase:" + (raw_id.split(":"))[1]
    thing = Gene(id=id, provided_by=row["provided_by"], category="biolink:Gene")
elif prefix == "WB":
    id = "WormBase:" + (raw_id.split(":"))[1]
    thing = Gene(id=id, provided_by=row["provided_by"], category="biolink:Gene")
elif prefix == "POMBASE":
    id = "PomBase:" + (raw_id.split(":"))[2]
    thing = Gene(id=id, provided_by=row["provided_by"], category="biolink:Gene")
elif prefix == "UniProtKB":
    thing = Protein(id=row["id"], provided_by=row["provided_by"], category="biolink:Protein")
elif prefix in ["DICTYBASE.GENE", "TAIR.LOCUS"]:
    id = str(row["id"]).replace(".", "_")
    thing = Gene(id=id, provided_by=row["provided_by"], category="biolink:Gene")
elif prefix in ["SGD", "RGD", "XENBASE", "ZFIN"]:
    thing = Gene(id=row["id"], provided_by=row["provided_by"], category="biolink:Gene")
else:
    thing = NamedThing(id=row["id"], provided_by=row["provided_by"], category="biolink:NamedThing")

koza_app.write(thing)
