import uuid

from biolink_model_pydantic.model import ( #type: ignore
    ChemicalMixture,
    Drug
)

from koza.cli_runner import get_koza_app #type: ignore

source_name="drugcentral-approval"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
if str(row['type'].strip()) == 'FDA':
    drug = Drug(id='DrugCentral:' + row["struct_id"],
                highest_FDA_approval_status="Approved")
    koza_app.write(drug)
