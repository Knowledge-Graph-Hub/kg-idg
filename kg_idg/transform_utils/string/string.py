import os
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Ingest KGX-format human protein-protein interactions from
STRING. Filter by interaction confidence
(combined score >= CONFIDENCE_THRESHOLD) to reduce noise.
Transform with KGX for validation.
"""

CONFIDENCE_THRESHOLD = 700

STRING_SOURCES = {"STRINGNodes": "string_nodes.tsv", "STRINGEdges": "string_edges.tsv"}


class STRINGTransform(Transform):
    """Ingests the STRING human subset transform from KG-COVID-19 and
    runs a kgx transform for validation.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "string"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(
        self, nodes_file: Optional[str] = None, edges_file: Optional[str] = None
    ) -> None:  # type: ignore
        """Obtain files and call the parse function."""
        if nodes_file and edges_file:
            for source in [nodes_file, edges_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in STRING_SOURCES.keys():
                name = STRING_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def filter(self, name: str, data_file: str) -> None:
        """
        Do quality screen here - combined score must be >=
        CONFIDENCE_THRESHOLD value.
        Also adds NamedThing to Biolink categories in nodefile.
        """

        new_edge_file_path = os.path.join(os.path.dirname(data_file), "string_edges_filtered.tsv")

        print(f"Applying confidence threshold of {CONFIDENCE_THRESHOLD} to STRING")
        with open(new_edge_file_path, "w") as new_edge_file, open(data_file, "r") as raw_edge_file:
            new_edge_file.write(raw_edge_file.readline())  # Header
            for line in raw_edge_file:
                scores = ((line.rstrip()).split("\t"))[6:]
                score_sum = sum([int(i) for i in scores if i.isdigit()])
                if score_sum >= CONFIDENCE_THRESHOLD:
                    new_edge_file.write(line)

        os.rename(data_file, os.path.join(os.path.dirname(data_file), "string_edges_full.tsv"))
        os.rename(
            new_edge_file_path,
            os.path.join(os.path.dirname(data_file), STRING_SOURCES["STRINGEdges"]),
        )

    def add_biolink_cat(self, name: str, data_file: str) -> None:
        """
        Adds the NamedThing Biolink category to nodes.
        """

        new_node_file_path = os.path.join(os.path.dirname(data_file), "string_nodes_updated.tsv")

        with open(new_node_file_path, "w") as new_node_file, open(data_file, "r") as raw_node_file:
            new_node_file.write(raw_node_file.readline())  # Header
            for line in raw_node_file:
                splitline = (line.rstrip()).split("\t")
                splitline[2] = splitline[2] + "|biolink:NamedThing"
                new_node_file.write("\t".join(splitline) + "\n")

        os.rename(data_file, os.path.join(os.path.dirname(data_file), "string_nodes_full.tsv"))
        os.rename(
            new_node_file_path,
            os.path.join(os.path.dirname(data_file), STRING_SOURCES["STRINGNodes"]),
        )

    def parse(self, name: str, data_file: str, source: str) -> None:
        print(f"Parsing {data_file}")

        if name == STRING_SOURCES["STRINGEdges"]:
            print(f"Parsing edges in {name}")
            self.filter(name, data_file)

        if name == STRING_SOURCES["STRINGNodes"]:
            print(f"Updating Biolink categories in {name}")
            self.add_biolink_cat(name, data_file)

        transform(
            inputs=[data_file],
            input_format="tsv",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
        )
