from biolink.model import Protein  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "tcrd-ids"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

xref_list = []
xref_types = {"HGNC:": "HGNC Symbol", "NCBIGene:": "NCBI Gene ID", "STRING:": "STRING ID"}
for xref_type in xref_types:
    value = row[xref_types[xref_type]]
    value = value.replace("/", "_")  # Gotta handle illegal slashes
    if str(value) == "None":
        continue
    else:
        xref_list.append(xref_type + str(value))

# Entities
protein = Protein(
    id="UniProtKB:" + row["UniProt"],
    description=row["Description"],
    provided_by="TCRD",
    xref=xref_list,
    type=row["TDL"],
    category="biolink:Protein",
)

koza_app.write(protein)
