import uuid

from biolink_model_pydantic.model import (
    ChemicalEntity,
    Pathway,
    ChemicalToPathwayAssociation,
    Predicate,
)

from koza.cli_runner import koza_app

source_name="chebi2reactome"

row = koza_app.get_row(source_name)

# Entities
chemical = ChemicalEntity(id='CHEBI:' + row['CHEBI_ID'])
pathway = Pathway(id='REACT:' + row['REACT_PATH_ID'])

# Association
association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=chemical.id,
    predicate=Predicate.participates_in,
    object=pathway.id,
    relation = koza_app.translation_table.resolve_term("pathway"),
    provided_by="reactome"
)

koza_app.write(chemical, association, pathway)
