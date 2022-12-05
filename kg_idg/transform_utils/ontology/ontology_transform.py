import os
from typing import Optional

from kgx.cli.cli_utils import transform  # type: ignore

from kg_idg.transform_utils.transform import Transform

ONTOLOGIES = {
    "ChebiTransform": "chebi_kgx_tsv.tar.gz",
    "HPOTransform": "hp_kgx_tsv.tar.gz",
    "GOTransform": "go_kgx_tsv.tar.gz",
    "MondoTransform": "mondo_kgx_tsv.tar.gz",
    "OGMSTransform": "ogms_kgx_tsv.tar.gz",
}


class OntologyTransform(Transform):
    """
    OntologyTransform acts as a passthrough for OBO ontologies -
    those retrieved as tsv node and edge lists in .tar.gz can be
    parsed directly by KGX.
    We have KGX decompress the file.
    """

    def __init__(self, input_dir: str = None, output_dir: str = None):
        source_name = "ontologies"
        super().__init__(source_name, input_dir, output_dir)

    def run(self, data_file: Optional[str] = None) -> None:
        """Method is called and performs needed transformations to process
        an ontology.
        Args:
            data_file: data file (.tar.gz) to parse
        Returns:
            None.
        """
        if data_file:
            k = data_file.split(".")[0]
            data_file = os.path.join(self.input_base_dir, data_file)
            self.parse(k, data_file, k)
        else:
            # load all ontologies
            for k in ONTOLOGIES.keys():
                data_file = os.path.join(self.input_base_dir, ONTOLOGIES[k])
                self.parse(k, data_file, k)

    def parse(self, name: str, data_file: str, source: str) -> None:
        """Processes the data_file.
        Args:
            name: Name of the ontology
            data_file: data file to parse
            source: Source name
        Returns:
             None.
        """
        print(f"Parsing {data_file}")

        transform(
            inputs=[data_file],
            input_format="tsv",
            input_compression="tar.gz",
            output=os.path.join(self.output_dir, name),
            output_format="tsv",
        )

        # Need to save this table for DrugCentral Tx
        if name in ["hp_kgx_tsv", "mondo_kgx_tsv"]:
            print("Writing UMLS to ontology ID map...")
            self.write_xref_map(name)

    def write_xref_map(self, name: str) -> None:
        """
        Set up a map of UMLS to ontology IDs.
        """
        shortname = (name.split("_"))[0]
        curie_prefix = shortname.upper()
        xref_map_path = \
            f"./kg_idg/transform_utils/drug_central/umls-cui_to_{shortname}_map.tsv"
        with open(f"./data/transformed/ontologies/{name}_nodes.tsv") as infile:
            with open(xref_map_path, "w") as outfile:
                infile.readline()  # Skip header
                for line in infile:
                    have_ids = False
                    umls_cui = ""
                    onto_id = ""
                    splitline = ((line).rstrip()).split("\t")
                    if splitline[0].startswith(curie_prefix):
                        onto_id = splitline[0]
                        xrefs = splitline[4].split("|")
                        for xref in xrefs:
                            if xref.startswith("UMLS"):
                                umls_cui = xref
                                have_ids = True
                                break
                        if have_ids:
                            outfile.write(f"{umls_cui}\t{onto_id}\n")
