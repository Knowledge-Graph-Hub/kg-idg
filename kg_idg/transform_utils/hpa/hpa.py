import os
import zipfile
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
HPA is the Human Protein Atlas.
We use its data to obtain sets of proteins with
tissue-specific expression.
See details on source files here:
https://www.proteinatlas.org/about/download
"""

HPA_SOURCES = {
    "HPA_DATA": "proteinatlas.tsv.zip",
}

HPA_CONFIGS = {
    "HPA_DATA": "hpa-data.yaml",
}


TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"


class ProteinAtlasTransform(Transform):
    """This transform ingests the tab-delimited HPA file.
    It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "hpa"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, hpa_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the HPA for Koza and call the parse function.
        """
        if hpa_file:
            for source in [hpa_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in HPA_SOURCES.keys():
                name = HPA_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform HPA file with Koza.
        Need to decompress it first.
        """
        print(f"Parsing {data_file}")
        config = os.path.join("kg_idg/transform_utils/hpa/", HPA_CONFIGS[source])
        output = self.output_dir

        # Decompress
        with zipfile.ZipFile(data_file, "r") as data_file_zip:
            data_file_zip.extractall(self.input_base_dir)

        # If source is unknown then we aren't going to guess
        if source not in HPA_CONFIGS:
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

        os.remove(data_file[:-4])  # Compressed source is a zip of a tsv
