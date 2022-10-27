import gzip
import os
import shutil
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform

"""
ATC is the Anatomical Therapeutic Chemical Classification.
We use it to categorize relationships among classes of drugs,
with codes provided by DrugCentral.
See details on source files here:
https://bioportal.bioontology.org/ontologies/ATC/?p=summary
"""

ATC_SOURCES = {
    "ATC_DATA": "atc.csv.gz",
}

ATC_CONFIGS = {
    "ATC_DATA": "atc-classes.yaml",
}

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"


class ATCTransform(Transform):
    """This transform ingests the ATC CSV file.
    It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "atc"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, atc_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the ATC for Koza and call the parse function.
        """
        if atc_file:
            for source in [atc_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in ATC_SOURCES.keys():
                name = ATC_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform ATC file with Koza.
        Need to decompress it first.
        """
        print(f"Parsing {data_file}")
        config = os.path.join("kg_idg/transform_utils/atc/", ATC_CONFIGS[source])
        output = self.output_dir

        # Decompress
        outname = name[:-3]
        outpath = os.path.join(self.input_base_dir, outname)
        with gzip.open(data_file, "rb") as data_file_gz:
            with open(outpath, "wb") as data_file_new:
                shutil.copyfileobj(data_file_gz, data_file_new)

        # If source is unknown then we aren't going to guess
        if source not in ATC_CONFIGS:
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

        os.remove(outpath)
