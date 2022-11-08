from biolink.model import Drug  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

"""The structures table contains details on each
   DrugCentral drug, including its chemical structure."""

source_name = "drugcentral-structures"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
drug = Drug(id="DrugCentral:" + row["id"],
            description=row["name"],
            category="biolink:Drug")

koza_app.write(drug)
