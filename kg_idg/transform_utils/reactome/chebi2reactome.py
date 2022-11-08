import uuid

from biolink.model import (  # type: ignore
    ChemicalEntity,
    ChemicalToPathwayAssociation,
    Pathway,
)
from koza.cli_runner import get_koza_app  # type: ignore

source_name = "chebi2reactome"
full_source_name = "Reactome"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
chemical = ChemicalEntity(id="CHEBI:" + row["CHEBI_ID"], category="biolink:ChemicalEntity")
pathway = Pathway(
    id="REACT:" + row["REACT_PATH_ID"], provided_by=full_source_name, category="biolink:Pathway"
)

# Association
association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=chemical.id,
    predicate="biolink:participates_in",
    object=pathway.id,
    aggregator_knowledge_source=full_source_name,
)

koza_app.write(chemical, association, pathway)
