import os
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Ingest gene to disease relationships from OMIM.
This is a passthrough transform using sources
from Monarch converted to KGX TSV.
"""

OMIM_NT_FILENAMES = ["omim_gtd_nodes.tsv", "omim_gtd_edges.tsv"]


class OMIMTransform(Transform):
    """This transform ingests the OMIM files."""

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "omim"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[str] = None) -> None:
        """Method is called and performs needed transformations to process
        OMIM files.
        Args:
            data_file: data files to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split(".")[0]
            entries = [os.path.join(self.input_base_dir, entry) for entry in data_file]
            self.parse(k, entries, k)
        else:
            entries = [os.path.join(self.input_base_dir, entry) for entry in OMIM_NT_FILENAMES]
            self.parse("omim", entries, "omim")

    def parse(self, name: str, data_file: list, source: str) -> None:
        """Processes the data_file.
        Args:
            name: Name of the source
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """
        print(f"Parsing {data_file}")

        transform(
            inputs=data_file,
            input_format="tsv",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
        )
