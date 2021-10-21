import uuid

#Doing some rough modeling for TCRD categories for now

from biolink_model_pydantic.model import Gene #type: ignore
from biolink_model_pydantic.model import Attribute #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="tcrd-ids"

row = koza_app.get_row(source_name)

# Entities
gene = Gene(id='NCBIGene:' + row['NCBI Gene ID'], #Best option for Biolink
            name= row['Name'],
            in_taxon= 'NCBITaxon:9606')

# TODO: Include the TDL in 
koza_app.write(gene)
