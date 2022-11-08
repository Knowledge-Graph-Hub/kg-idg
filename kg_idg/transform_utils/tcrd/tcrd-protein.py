from biolink.model import Protein  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

# Most TCRD protein info comes from the tcrd-ids transform.
# This transform ensures all protein IDs are included.
# The input file contains protein families
# (I think they're from UniProt, based on the language)
# but we don't transform them here.

source_name = "tcrd-protein"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
protein = Protein(id="UniProtKB:" + row["uniprot"], provided_by="TCRD", category="biolink:Protein")

koza_app.write(protein)
