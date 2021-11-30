import uuid

from biolink_model_pydantic.model import ( #type: ignore
    ChemicalMixture,
    Drug
)

from koza.cli_runner import koza_app #type: ignore

source_name="drugcentral-approval"

row = koza_app.get_row(source_name)

# Entities
if str(row['type'].strip()) == 'FDA':
    drug = Drug(id='DrugCentral:' + row["id"],
                highest_FDA_approval_status="Approved")
    koza_app.write(drug)
