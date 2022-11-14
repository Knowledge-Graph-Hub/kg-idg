from biolink.model import Pathway  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "reactomepathways"
full_source_name = "Reactome"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
pathway = Pathway(
    id="REACT:" + row["REACT_PATH_ID"],
    description=row["REACT_NAME"],
    provided_by=full_source_name,
    category="biolink:Pathway",
)

koza_app.write(pathway)
