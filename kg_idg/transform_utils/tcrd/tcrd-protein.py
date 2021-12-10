import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Protein,
)

from koza.cli_runner import koza_app #type: ignore

# Most TCRD protein info comes from the tcrd-ids transform.
# This transform ensures all protein IDs are included.
# The input file contains protein families
# (I think they're from UniProt, based on the language)
# but we don't transform them here.

source_name="tcrd-protein"

row = koza_app.get_row(source_name)

# Entities
protein = Protein(id='UniProtKB:' + row['uniprot'],
                    source='TCRD')

koza_app.write(protein)
