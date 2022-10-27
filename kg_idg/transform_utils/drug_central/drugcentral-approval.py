from biolink.model import Drug  # type: ignore
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "drugcentral-approval"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
if str(row["type"].strip()) == "FDA":
    drug = Drug(
        id="DrugCentral:" + row["struct_id"],
        highest_FDA_approval_status="Approved",
        category="biolink:Drug",
    )
    koza_app.write(drug)
