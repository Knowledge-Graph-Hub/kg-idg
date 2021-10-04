import uuid

from biolink_model_pydantic.model import (
    Protein,
    Pathway,
    ChemicalToPathwayAssociation,
    Predicate,
)
from koza.manage.data_collector import write
from koza.manager.data_provider import inject_row, inject_translation_table

source_name="uniprot2reactome"

translation_table = inject_translation_table()

row = inject_row(source_name)

# Entities
protein = Protein(id='UniProtKB:' + row['UPID'])
pathway = Pathway(id='REACT:' + row['REACT_PATH_ID'])

# Association
association = ChemicalToPathwayAssociation(
    id="uuid:" + str(uuid.uuid1()),
    subject=chemical.id,
    predicate=Predicate.participates_in,
    object=pathway.id,
    relation = translation_table.resolve_term("participates in")
)

koza_app.write(protein, association, pathway)
