import csv
import gzip
import os
import shutil
import sys
from typing import Optional

from koza.cli_runner import transform_source  # type: ignore

from kg_idg.transform_utils.transform import Transform
from kg_idg.utils.sql_utils import process_data_dump

"""
DrugCentral provides a set of drug vs. target interactions.
We integrate this data with TRCD contents.
See all available files here:
https://unmtid-shinyapps.net/download/DrugCentral/
"""

DRUG_CENTRAL_SOURCES = {
    "DrugCentralDTI": "drug.target.interaction.tsv.gz",
    "DrugCentralDB": "drugcentral.dump.sql.gz",
}

DRUG_CENTRAL_CONFIGS = {
    "DrugCentralDTI": "drugcentral-dti.yaml",
    "DrugCentralDB": "drugcentral-{table}.yaml",
}

# Reference table must be loaded before property table due to dependency
WANTED_TABLES = ["approval",
                 "atc_ddd",
                 "identifier",
                 "omop_relationship",
                 "reference",
                 "property",
                 "structures",
                 ]

TRANSLATION_TABLE = "./kg_idg/transform_utils/translation_table.yaml"
REFERENCE_MAP_TABLE = "./kg_idg/transform_utils/drug_central/drugcentral-reference_map.tsv"


class DrugCentralTransform(Transform):
    """This transform ingests the tab-delimited DrugCentral
    drug-target interactions file.
        It is transformed to KGX-format node and edge lists.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None) -> None:
        source_name = "drug_central"
        super().__init__(source_name, input_dir, output_dir)  # set some variables

    def run(self, dc_file: Optional[str] = None) -> None:  # type: ignore
        """
        Set up the DrugCentral file for Koza and call the parse function.
        """
        if dc_file:
            for source in [dc_file]:
                k = source.split(".")[0]
                data_file = os.path.join(self.input_base_dir, source)
                self.parse(k, data_file, k)
        else:
            for k in DRUG_CENTRAL_SOURCES.keys():
                name = DRUG_CENTRAL_SOURCES[k]
                data_file = os.path.join(self.input_base_dir, name)
                self.parse(name, data_file, k)

    def write_reference_map(self) -> None:
        """
        Sets up references as a map so their database IDs can be used
        to look up their URIs (i.e., URLs or CURIEs).
        """
        with open("./data/transformed/drug_central/drugcentral-reference.tsv") as infile:
            with open(REFERENCE_MAP_TABLE, "w") as outfile:
                infile.readline()  # Skip header
                for line in infile:
                    db_id = ""
                    uri = ""
                    ref_type = ""
                    splitline = ((line).rstrip()).split("\t")
                    if splitline[0] == '"':  # it's empty
                        continue
                    db_id = splitline[0]
                    ref_type = splitline[4]
                    if ref_type == "JOURNAL ARTICLE":
                        if splitline[1] == "":
                            uri = "DOI:" + splitline[2]
                        else:
                            uri = "PMID:" + splitline[1]
                    elif ref_type == "BOOK":
                        uri = "isbn:" + splitline[7]
                    elif ref_type in ["CLINICAL TRIAL", "DRUG LABEL", "ONLINE RESOURCE"]:
                        uri = splitline[8]
                    elif ref_type == "PATENT":
                        uri = "GOOGLE_PATENT:" + (splitline[3]).replace(" ", "")
                    else:
                        uri = splitline[3]
                    outfile.write(f"{db_id}\t{uri}\n")

    def preprocess_structures(self, source_path: str) -> None:
        """
        Structures table needs some pre-processing due to one column being image data
        so it's generally too large to parse without specifying a size limit for csv
        Load the tsv with csv, remove the offending column,
        and write the new tsv
        :param source_path: str, path to the structures tsv
        """
        print("Pre-processing DrugCentral structures table before transform...")
        temp_tsv_path = source_path + ".temp"
        #
        csv.field_size_limit(
            sys.maxsize
        )  # The issue is oversize values, so we accomodate this time
        with open(source_path, "r") as infile, open(temp_tsv_path, "w") as outfile:
            read_tsv = csv.reader(infile, delimiter="\t")
            write_tsv = csv.writer(outfile, delimiter="\t")
            header = next(read_tsv)
            write_tsv.writerow(header)
            i = 1
            for line in read_tsv:
                line[22] = "NA"
                write_tsv.writerow(line)
                i = i + 1

        shutil.move(temp_tsv_path, source_path)
        print("Complete.")

    def parse(self, name: str, data_file: str, source: str) -> None:
        """
        Transform DrugCentral file with Koza.
        Need to decompress it first.
        """
        print(f"Parsing {data_file}")

        # Decompress
        outname = name[:-3]
        outpath = os.path.join(self.input_base_dir, outname)
        with gzip.open(data_file, "rb") as data_file_gz:
            with open(outpath, "wb") as data_file_new:
                shutil.copyfileobj(data_file_gz, data_file_new)

        # If source is unknown then we aren't going to guess
        if source not in DRUG_CENTRAL_CONFIGS:
            raise ValueError(f"Source file {source} not recognized - not transforming.")

        if outname[-3:] == "sql":
            """
            This is the full SQL dump so we need to load it as a local database,
            export it as individual TSVs,
            then pass what we want to Koza transform_source.
            """
            print("Transforming data dump to TSV. This may take a while...")
            if not process_data_dump(
                "drugcentral",
                "postgres",
                outpath,
                WANTED_TABLES,
                self.input_base_dir,
                self.output_dir,
                list_tables=False,
            ):
                print("Did not process DrugCentral data dump!")
                return

        output = self.output_dir
        if source == "DrugCentralDB":  # Configs vary by DB table
            for table in WANTED_TABLES:
                config = os.path.join(
                    "kg_idg/transform_utils/drug_central/", f"drugcentral-{table}.yaml"
                )

                if table == "structures":
                    self.preprocess_structures(
                        source_path="./data/transformed/drug_central/drugcentral-structures.tsv"
                    )

                print(f"Transforming to {output} using source in {config}")
                transform_source(
                    source=config,
                    output_dir=output,
                    output_format="tsv",
                    global_table=TRANSLATION_TABLE,
                    local_table=None,
                )
                if table == "reference":  # Need to save this table for lookup later
                    print("Writing reference ID map...")
                    self.write_reference_map()

        else:
            config = os.path.join(
                "kg_idg/transform_utils/drug_central/", DRUG_CENTRAL_CONFIGS[source]
            )
            print(f"Transforming to {output} using source in {config}")
            transform_source(
                source=config,
                output_dir=output,
                output_format="tsv",
                global_table=TRANSLATION_TABLE,
                local_table=None,
            )

        os.remove(outpath)
