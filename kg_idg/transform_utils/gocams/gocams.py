import os
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Ingest GOCAMs from KG-COVID-19.
Moves them to the transformed data directory.
"""

GOCAM_SOURCES = {"GOCAMsNodes": "GOCAMs_nodes.tsv", "GOCAMsEdges": "GOCAMs_edges.tsv"}

GOCAM_CONFIGS = {"GOCAMsNodes": "gocams-fix-nodes.yaml", "GOCAMsEdges": "gocams-fix-edges.yaml"}

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"


class GOCAMTransform(Transform):
    """This transform ingests the GOCAMs transform from KG-COVID-19 and
    transforms it further with Koza.
    The CAMs are already in KGX format but require some
    tweaking for model alignment.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "gocams"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(
        self, nodes_file: Optional[str] = None, edges_file: Optional[str] = None
    ) -> None:  # type: ignore
        """
        Set up for Koza and call the parse function.
        """
        if nodes_file and edges_file:
            for source in [nodes_file, edges_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in GOCAM_SOURCES.keys():
                name = GOCAM_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform GOCAM edge and node files with Koza.
        """
        print(f"Parsing {data_file}")

        output = self.output_dir
        config = os.path.join("kg_idg/transform_utils/gocams/", GOCAM_CONFIGS[source])

        transform_source(
            source=config,
            output_dir=output,
            output_format="tsv",
            global_table=TRANSLATION_TABLE,
            local_table=None,
        )
