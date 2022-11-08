import gzip
import os
import shutil
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform
from kg_idg.utils.sql_utils import process_data_dump

"""
TCRD is the Target Central Resource Database.
We use this data for the ID mappings necessary to integrate
with Pharos.
We also download the full MySQL dump and convert it to TSV
(rather than trying to re-load the whole DB).
See details on source files here:
http://juniper.health.unm.edu/tcrd/download/README
"""

# TCRD_SOURCES = {"TCRD-IDs": "TCRDv6.12.4.tsv", "TCRD-DB": "tcrd.sql.gz"}
TCRD_SOURCES = {"TCRD-IDs": "TCRDv6.12.4.tsv"}

TCRD_CONFIGS = {
    "TCRD-IDs": "tcrd-ids.yaml",
    "TCRD-DB": "tcrd-{table}.yaml",
}

# Some of these tables need to be transformed as they're
# referenced by others (e.g., data_type)
# but aren't really useful as transforms
# so we'll ignore them below
# WANTED_TABLES = ["data_type","info_type","xref_type",
#                "protein","target","tdl_info","drug_activity",
#                "feature","mondo","mondo_parent",
#                "mondo_xref","pubmed","protein2pubmed"]
WANTED_TABLES = ["data_type", "info_type", "xref_type", "protein"]

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"


class SplitterArgs:
    # Setup for the MySQL parser
    def __init__(self):
        pass


class TCRDTransform(Transform):
    """This transform ingests the tab-delimited TCRD ID mapping file.
    It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "tcrd"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, tcrd_id_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the TCRD ID file for Koza and call the parse function.
        """
        if tcrd_id_file:
            for source in [tcrd_id_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in TCRD_SOURCES.keys():
                name = TCRD_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform TCRD ID mapping file with Koza.
        Removes uncompressed raw file when finished.
        """
        print(f"Parsing {data_file}")

        outname = name[:-3]

        need_to_remove_raw_source = False

        # Decompress
        if name[-2:] == "gz":
            need_to_remove_raw_source = True
            outpath = os.path.join(self.input_base_dir, outname)
            with gzip.open(data_file, "rb") as data_file_gz:
                with open(outpath, "wb") as data_file_new:
                    shutil.copyfileobj(data_file_gz, data_file_new)

        # If source is unknown then we aren't going to guess
        if source not in TCRD_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")

        if outname[-3:] == "sql":
            """
            This is the full SQL dump so we need to load it as a local database,
            export it as individual TSVs,
            then pass what we want to Koza transform_source.
            """
            print("Transforming MySQL dump to TSV. This may take a while...")
            if not process_data_dump(
                "tcrd",
                "mysql",
                outpath,
                WANTED_TABLES,
                self.input_base_dir,
                self.output_dir,
                list_tables=False,
            ):
                print("Did not process TCRD MySQL dump!")
                return

        output = self.output_dir
        if source == "TCRD-DB":
            for table in WANTED_TABLES:
                if table in ["data_type", "info_type", "xref_type"]:
                    continue
                else:
                    config = os.path.join("kg_idg/transform_utils/tcrd/", f"tcrd-{table}.yaml")
                    print(f"Transforming to {output} using source in {config}")
                    transform_source(
                        source=config,
                        output_dir=output,
                        output_format="tsv",
                        global_table=TRANSLATION_TABLE,
                        local_table=None,
                    )
        else:
            config = os.path.join("kg_idg/transform_utils/tcrd/", TCRD_CONFIGS[source])
            print(f"Transforming to {output} using source in {config}")
            transform_source(
                source=config,
                output_dir=output,
                output_format="tsv",
                global_table=TRANSLATION_TABLE,
                local_table=None,
            )

        if need_to_remove_raw_source:
            os.remove(outpath)
