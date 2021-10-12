import uuid

from biolink_model_pydantic.model import Gene #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="tcrd-ids"

row = koza_app.get_row(source_name)

# Entities
gene = Gene(id='NCBIGene:' + row['NCBI Gene ID'], #Consider other primary ID?
            name= row['Name'])

koza_app.write(gene)
