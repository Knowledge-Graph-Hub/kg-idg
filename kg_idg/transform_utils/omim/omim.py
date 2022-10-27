import os
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Ingest gene to disease relationships from OMIM.
The source document is in n-triple format provided by Monarch.

"""

OMIM_NT_FILENAME = "omim.nt"


class OMIMTransform(Transform):
    """This transform ingests the OMIM nt file and parses it to KGX tsv format."""

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "omim"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[str] = None) -> None:
        """Method is called and performs needed transformations to process
        OMIM n-triples.
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
            data_file = os.path.join(self.input_base_dir, OMIM_NT_FILENAME)
            self.parse("omim", data_file, OMIM_NT_FILENAME)

    def parse(self, name: str, data_file: str, source: str) -> None:
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
            inputs=[data_file],
            input_format="nt",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
        )
