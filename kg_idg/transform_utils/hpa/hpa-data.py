import uuid

from biolink_model_pydantic.model import Gene #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="hpa-data"

row = koza_app.get_row(source_name)

# Entities
gene = Gene(id='ENSEMBL:' + row['Ensembl'],
            name= row['Gene'])

koza_app.write(gene)
