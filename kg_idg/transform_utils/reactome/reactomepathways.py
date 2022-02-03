import uuid

from biolink_model_pydantic.model import Pathway #type: ignore

from koza.cli_runner import koza_app #type: ignore

source_name="reactomepathways"
full_source_name="Reactome"

row = koza_app.get_row(source_name)

# Entities
pathway = Pathway(id='REACT:' + row['REACT_PATH_ID'],
                    description= row['REACT_NAME'],
                    source=full_source_name)

koza_app.write(pathway)
