import os

from typing import Optional
from kgx.cli.cli_utils import transform  # type: ignore
from kg_idg.transform_utils.transform import Transform

# TODO: the file names for these on KG-OBO will soon be of format 
# '[obo_name]_kgx_tsv.at.gz'

ONTOLOGIES = {
    'ChebiTransform': 'chebi.tar.gz',
    'HPOTransform': 'hp.tar.gz',
    'GOTransform': 'go.tar.gz',
    'MondoTransform': 'mondo.tar.gz',
    'OGMSTransform': 'ogms.tar.gz'
}


class OntologyTransform(Transform):
    """
    OntologyTransform acts as a passthrough for OBO ontologies - 
    those retrieved as tsv node and edge lists in .tar.gz can be
    parsed directly by KGX. 
    We have KGX decompress the file.
    """
    def __init__(self, input_dir: str = None, output_dir: str = None):
        source_name = "ontologies"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[str] = None) -> None:
        """Method is called and performs needed transformations to process
        an ontology.
        Args:
            data_file: data file (.tar.gz) to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split('.')[0]
            data_file = os.path.join(self.input_base_dir, data_file)
            self.parse(k, data_file, k)
        else:
            # load all ontologies
            for k in ONTOLOGIES.keys():
                data_file = os.path.join(self.input_base_dir, ONTOLOGIES[k])
                self.parse(k, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Processes the data_file.
        Args:
            name: Name of the ontology
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """
        print(f"Parsing {data_file}")

        transform(inputs=[data_file],
                  input_format='tsv',
                  input_compression='tar.gz',
                  output=os.path.join(self.output_dir, name),
                  output_format='tsv')
