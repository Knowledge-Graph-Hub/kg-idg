import uuid

from biolink_model_pydantic.model import Protein #type: ignore
from biolink_model_pydantic.model import Attribute #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="tcrd-ids"

row = koza_app.get_row(source_name)

# Entities
protein = Protein(id='UniProtKB:' + row['UniProt'],
            description= row['Description'],
            in_taxon= 'NCBITaxon:9606',
            source='TCRD')

koza_app.write(protein)
