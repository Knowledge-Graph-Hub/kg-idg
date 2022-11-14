import os
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Ingest gene to disease
and phenotype to disease
relationships from Orphanet.

"""

ORPHANET_CONFIGS = {
    "orphanet_gene.xml": "orphanet_gene.yaml",
    "orphanet_pheno.xml": "orphanet_pheno.yaml",
}

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"

PREPROCESS_PATH = "/kg_idg/transform_utils/orphanet/preprocess_orphanet.sh"


class OrphanetTransform(Transform):
    """This transform ingests the Orphanet files and parses them to KGX tsv format."""

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "orphanet"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[list] = None) -> None:
        """Method is called and performs needed transformations to process
        Orphanet files.
        Args:
            data_file: list of data files to parse
        Returns:
            None.
        """
        if data_file:
            for entry in data_file:
                k = entry.split(".")[0]
                entry = os.path.join(self.input_base_dir, entry)
                self.parse(k, entry, k)
        else:
            for entry in ORPHANET_CONFIGS:
                name = ORPHANET_CONFIGS[entry]
                entry = os.path.join(self.input_base_dir, entry)
                self.parse(name, entry, name)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Processes the data_file.
        Args:
            name: Name of the source
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """
        print(f"Parsing {data_file} to JSON...")
        config = os.path.join("kg_idg/transform_utils/orphanet/", source)
        output = self.output_dir

        # Preprocess XML to JSON for easier parsing.
        os.system(f".{PREPROCESS_PATH}")

        print(f"Transforming using source in {config}")
        transform_source(
            source=config,
            output_dir=output,
            output_format="tsv",
            global_table=TRANSLATION_TABLE,
            local_table=None,
        )
