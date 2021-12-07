import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Protein,
    GeneFamily,
    DrugToGeneAssociation,
    Predicate,
    Attribute
)

from koza.cli_runner import koza_app #type: ignore

# Most TCRD protein info comes from the tcrd-ids transform.
# This transform ensures all protein IDs are included,
# and additionally provides protein families.

source_name="tcrd-protein"

row = koza_app.get_row(source_name)

# Entities
protein = Protein(id='UniProtKB:' + row['uniprot'],
                    source='TCRD')

koza_app.write(protein)
