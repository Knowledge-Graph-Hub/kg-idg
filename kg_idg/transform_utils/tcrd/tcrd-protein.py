import uuid

#Doing some rough modeling for TCRD categories for now

from biolink_model_pydantic.model import Protein #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="tcrd-protein"

row = koza_app.get_row(source_name)

# Entities
protein = Protein(id='DrugCentral:' + row['id'],
            name= row['name'])

koza_app.write(protein)
