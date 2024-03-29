import os
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
uPheno2 is a community-curated ontology for the
representation and integration of phenotypes across species.
See here for more details re: the other ontologies involved:
https://github.com/obophenotype/upheno/wiki/Phenotype-Ontologies-Reconciliation-Effort
We obtain it as OWL so it requires specific transform with KGX.
"""

UPHENO_SOURCES = {
    "upheno2": "upheno_all_with_relations.owl",
}


class UPhenoTransform(Transform):
    def __init__(self, input_dir: str = None, output_dir: str = None):
        source_name = "upheno2"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[str] = None) -> None:
        """
        Method is called and performs needed transformations to process
        the ontology.
        Args:
            data_file: data file to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split(".")[0]
            data_file = os.path.join(self.input_base_dir, data_file)
            self.parse(k, data_file, k)
        else:
            for k in UPHENO_SOURCES.keys():
                data_file = os.path.join(self.input_base_dir, UPHENO_SOURCES[k])
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

        transform(
            inputs=[data_file],
            input_format="owl",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
        )
