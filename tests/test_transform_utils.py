import os
import shutil
from unittest import TestCase, mock, skip

from parameterized import parameterized

from kg_idg import download  # Need to download each source first
from kg_idg.transform_utils.atc.atc import ATCTransform
from kg_idg.transform_utils.drug_central.drug_central import DrugCentralTransform
from kg_idg.transform_utils.gocams.gocams import GOCAMTransform
from kg_idg.transform_utils.hpa.hpa import ProteinAtlasTransform
from kg_idg.transform_utils.omim.omim import OMIMTransform
from kg_idg.transform_utils.orphanet.orphanet import OrphanetTransform
from kg_idg.transform_utils.reactome.reactome import ReactomeTransform
from kg_idg.transform_utils.string.string import STRING_SOURCES, STRINGTransform

# from kg_idg.transform_utils.tcrd.tcrd import TCRDTransform
from kg_idg.transform_utils.upheno.upheno import UPhenoTransform
from kg_idg.utils.transform_utils import collapse_uniprot_curie, guess_bl_category

# Need to download or copy over some snippets due to hardcoded Koza paths
data_raw_path = "data/raw/"
download(yaml_file="download.yaml", output_dir=data_raw_path, snippet_only=True)
for source_snippet in [
    "atc.csv.gz",
    "drugcentral.dump.sql.gz",
    "drug.target.interaction.tsv.gz",
    "proteinatlas.tsv.zip",
    "tcrd.sql.gz",
]:
    shutil.copyfile(
        f"tests/resources/snippets/{source_snippet}", os.path.join(data_raw_path, source_snippet)
    )


class TestTransformUtils(TestCase):
    def setUp(self) -> None:
        self.input_dir = "tests/resources/snippets/"
        self.raw_path = data_raw_path
        self.output_dir = "tests/resources/"

    @parameterized.expand(
        [
            ["", "biolink:NamedThing"],
            ["UniProtKB", "biolink:Protein"],
            ["ComplexPortal", "biolink:Protein"],
            ["GO", "biolink:OntologyClass"],
        ]
    )
    def test_guess_bl_category(self, curie, category):
        self.assertEqual(category, guess_bl_category(curie))

    @parameterized.expand(
        [
            ["foobar", "foobar"],
            ["ENSEMBL:ENSG00000178607", "ENSEMBL:ENSG00000178607"],
            ["UniprotKB:P63151-1", "UniprotKB:P63151"],
            ["uniprotkb:P63151-1", "uniprotkb:P63151"],
            ["UniprotKB:P63151-2", "UniprotKB:P63151"],
        ]
    )
    def test_collapse_uniprot_curie(self, curie, collapsed_curie):
        self.assertEqual(collapsed_curie, collapse_uniprot_curie(curie))

    # Now start testing source-specific transform utils
    # Load pre-defined inputs and specific ones, for coverage

    # Filter test is included here
    def test_string_transform(self):
        t = STRINGTransform(self.input_dir, self.output_dir)
        nodes_path = STRING_SOURCES["STRINGNodes"]
        edges_path = STRING_SOURCES["STRINGEdges"]
        this_output_dir = os.path.join(self.output_dir, "string")
        t.run(nodes_file=nodes_path, edges_file=edges_path)
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    @skip("Test won't clear unless jq installed")
    def test_orphanet_transform(self):
        t = OrphanetTransform(self.input_dir, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "orphanet")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_omim_transform(self):
        t = OMIMTransform(self.input_dir, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "omim")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_gocams_transform(self):
        t = GOCAMTransform(self.input_dir, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "gocams")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_upheno_transform(self):
        t = UPhenoTransform(self.input_dir, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "upheno2")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    # Koza transforms

    # This transform requires a database load
    # but we test that elsewhere (in test_sql_utils)
    @mock.patch("koza.cli_runner.transform_source")
    def test_drug_central_transform(self, mock_transform_source):
        t = DrugCentralTransform(self.raw_path, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "drug_central")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_drug_central_structures_preprocessing(self):
        source = "./tests/resources/snippets/drugcentral-structures.tsv"
        t = DrugCentralTransform(self.raw_path, self.output_dir)
        t.preprocess_structures(source_path=source)
        self.assertTrue(os.path.exists(source))

    def test_reactome_transform(self):
        t = ReactomeTransform(self.raw_path, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "reactome")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    # Another database load
    # @mock.patch("koza.cli_runner.transform_source")
    # def test_tcrd_transform(self, mock_transform_source):
    #     t = TCRDTransform(self.raw_path, self.output_dir)
    #     this_output_dir = os.path.join(self.output_dir, "tcrd")
    #     t.run()
    #     self.assertTrue(os.path.exists(this_output_dir))
    #     shutil.rmtree(this_output_dir)

    def test_hpa_transform(self):
        t = ProteinAtlasTransform(self.raw_path, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "hpa")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_atc_transform(self):
        t = ATCTransform(self.raw_path, self.output_dir)
        this_output_dir = os.path.join(self.output_dir, "atc")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    @classmethod
    def tearDownClass(cls):
        """
        This removes all files from the data/raw dir!
        These tests download minimal versions of the raws,
        but must use the original location due to
        hardcoded Koza config files.
        So this cleans them out lest they get used
        in real transforms.
        """
        if os.path.exists(data_raw_path):
            shutil.rmtree(data_raw_path)
            os.makedirs(data_raw_path)
