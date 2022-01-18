
from biolink_model_pydantic.model import Drug #type: ignore

from koza.cli_runner import koza_app #type: ignore

'''The structures table contains details on each 
   DrugCentral drug, including its chemical structure.'''

source_name="drugcentral-structures"

row = koza_app.get_row(source_name)

# Entities
drug = Drug(id='DrugCentral:' + row["id"],
            description = row["name"],
            source="DrugCentral")

koza_app.write(drug)
