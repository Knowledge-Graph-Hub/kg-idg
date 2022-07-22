import uuid

from biolink_model_pydantic.model import ( #type: ignore
    Pathway,
    Association,
    Predicate,
)

from koza.cli_runner import get_koza_app #type: ignore

source_name="reactomepathwaysrelation"
full_source_name="Reactome"

koza_app = get_koza_app(source_name)
row = koza_app.get_row()

# Entities
parent_pathway = Pathway(id='REACT:' + row['REACT_PATH_ID'],
                    source=full_source_name)
child_pathway = Pathway(id='REACT:' + row['REACT_PATH_CHILD'])

# Association
association = Association(
    id="uuid:" + str(uuid.uuid1()),
    subject=parent_pathway.id,
    predicate=Predicate.contains_process,
    object=child_pathway.id,
    relation = "RO:0002351", #has_member,
    source=full_source_name
)

koza_app.write(parent_pathway, association, child_pathway)
