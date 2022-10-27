import os
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
Reactome provides mappings to pathways in TSVs.
Here, we transform the protein to pathway and CHEBI to pathway mappings
to edge and node lists.
See details on source files here:
https://reactome.org/download-data?id=86&ml=1
"""

REACTOME_SOURCES = {
    "ReactomePathways": "ReactomePathways.txt",
    "ReactomePathwayRelationships": "ReactomePathwaysRelation.txt",
    "ChEBI2Reactome": "ChEBI2Reactome_PE_Pathway.txt",
    "UniProt2Reactome": "UniProt2Reactome_PE_Pathway.txt",
}

REACTOME_CONFIGS = {
    "ReactomePathways": "reactomepathways.yaml",
    "ReactomePathwayRelationships": "reactomepathwaysrelation.yaml",
    "ChEBI2Reactome": "chebi2reactome.yaml",
    "UniProt2Reactome": "uniprot2reactome.yaml",
}

REACTOME_HEADERS = {
    "ReactomePathways": "REACT_PATH_ID\tREACT_NAME\tSPECIES\n",
    "ReactomePathwayRelationships": "REACT_PATH_ID\tREACT_PATH_CHILD\n",
    "ChEBI2Reactome":
        "CHEBI_ID\tREACT_PE_ID\tREACT_NAME\tREACT_PATH_ID\tURL\tEVENT_NAME\tEVIDENCE\tSPECIES\n",
    "UniProt2Reactome":
        "UPID\tREACT_PE_ID\tREACT_NAME\tREACT_PATH_ID\tURL\tEVENT_NAME\tEVIDENCE\tSPECIES\n",
}

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"


class ReactomeTransform(Transform):
    """This transform handles the Reactome pathway
    list and pathway relationship (parent/child) lists.
    Also ingests the Reactome Protein (UniProt) to
        pathway and CHEBI to pathway files:
        UniProt2Reactome_PE_Pathway.txt and
        ChEBI2Reactome_PE_Pathway.txt respectively.
        All are transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "reactome"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, react_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up Reactome files for Koza and call the parse function.
        """
        if react_file:
            for source in [react_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in REACTOME_SOURCES.keys():
                name = REACTOME_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform Reactome files with Koza.
        Need to append a header to each first for Koza to work properly.
        """
        print(f"Parsing {data_file}")
        config = os.path.join("kg_idg/transform_utils/reactome/", REACTOME_CONFIGS[source])
        output = self.output_dir

        # Write header, unless it's already there
        with open(data_file, "r") as infile:
            content = [line for line in infile]
        if content[0] != REACTOME_HEADERS[source]:
            with open(data_file, "w") as outfile:
                print(f"Writing header to {data_file}")
                outfile.write(REACTOME_HEADERS[source])
                for line in content:
                    outfile.write(line)

        # If source is unknown then we aren't going to guess
        if source not in REACTOME_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")
        else:
            print(f"Transforming using source in {config}")
            transform_source(
                source=config,
                output_dir=output,
                output_format="tsv",
                global_table=TRANSLATION_TABLE,
                local_table=None,
            )
