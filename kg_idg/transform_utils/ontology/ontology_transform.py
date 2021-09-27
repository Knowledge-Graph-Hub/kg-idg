import os

from typing import Optional

from kg_idg.transform_utils.transform import Transform

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
        if data_file.endswith('tar.gz'):
             compression = 'gz'
        else:
             compression = None
        output_transformer.save(filename=os.path.join(self.output_dir, f'{name}'), mode=None)
