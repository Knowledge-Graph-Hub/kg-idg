from unittest import TestCase, mock
import os
import shutil
from parameterized import parameterized
from kg_idg.utils.transform_utils import guess_bl_category, collapse_uniprot_curie
from kg_idg.transform_utils.orphanet.orphanet import OrphanetTransform, ORPHANET_NT_FILENAME
from kg_idg.transform_utils.omim.omim import OMIMTransform, OMIM_NT_FILENAME
from kg_idg.transform_utils.drug_central.drug_central import DrugCentralTransform, DRUG_CENTRAL_SOURCES
from kg_idg.transform_utils.string.string import STRINGTransform, STRING_SOURCES
from kg_idg.transform_utils.gocams.gocams import GOCAMTransform
from kg_idg.transform_utils.reactome.reactome import ReactomeTransform
from kg_idg.transform_utils.tcrd.tcrd import TCRDTransform
from kg_idg.transform_utils.hpa.hpa import ProteinAtlasTransform

class TestTransformUtils(TestCase):

    def setUp(self) -> None:
        self.input_dir = 'tests/resources/snippets/'
        self.output_dir = 'tests/resources/'

    @parameterized.expand([
        ['', 'biolink:NamedThing'],
        ['UniProtKB', 'biolink:Protein'],
        ['ComplexPortal', 'biolink:Protein'],
        ['GO', 'biolink:OntologyClass'],
    ])
    def test_guess_bl_category(self, curie, category):
        self.assertEqual(category, guess_bl_category(curie))

    @parameterized.expand([
        ['foobar', 'foobar'],
        ['ENSEMBL:ENSG00000178607', 'ENSEMBL:ENSG00000178607'],
        ['UniprotKB:P63151-1', 'UniprotKB:P63151'],
        ['uniprotkb:P63151-1', 'uniprotkb:P63151'],
        ['UniprotKB:P63151-2', 'UniprotKB:P63151'],
    ])
    def test_collapse_uniprot_curie(self, curie, collapsed_curie):
        self.assertEqual(collapsed_curie, collapse_uniprot_curie(curie))

    # Now start testing source-specific transform utils
    # Load pre-defined inputs and specific ones, for coverage
    def test_drug_central_transform(self):
        t = DrugCentralTransform(self.input_dir,self.output_dir)
        nodes_path = DRUG_CENTRAL_SOURCES["DrugCentralNodes"]
        edges_path = DRUG_CENTRAL_SOURCES["DrugCentralEdges"]
        this_output_dir = os.path.join(self.output_dir,"drug_central")
        t.run(nodes_file=nodes_path,edges_file=edges_path)
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    # Filter test is included here
    def test_string_transform(self):
        t = STRINGTransform(self.input_dir,self.output_dir)
        nodes_path = STRING_SOURCES["STRINGNodes"]
        edges_path = STRING_SOURCES["STRINGEdges"]
        this_output_dir = os.path.join(self.output_dir,"string")
        t.run(nodes_file=nodes_path,edges_file=edges_path)
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)
    
    def test_orphanet_transform(self):
        t = OrphanetTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"orphanet")
        t.run(data_file=ORPHANET_NT_FILENAME)
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_omim_transform(self):
        t = OMIMTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"omim")
        t.run(data_file=OMIM_NT_FILENAME)
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)

    def test_gocams_transform(self):
        t = GOCAMTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"gocams")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        shutil.rmtree(this_output_dir)
    
    # Koza transforms have hard-coded sources so we skip the transform
    # and instead ensure they don't proceed if source is incorrect
    # (Note that these tests will fail if a non-test transform has been run!)

    @mock.patch('koza.cli_runner.transform_source')
    def test_reactome_transform(self, mock_transform_source):
        t = ReactomeTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"reactome")
        with self.assertRaises(ValueError):
            t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        self.assertFalse(mock_transform_source.called)
        shutil.rmtree(this_output_dir)

    @mock.patch('koza.cli_runner.transform_source')
    def test_tcrd_transform(self, mock_transform_source):
        t = TCRDTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"tcrd")
        with self.assertRaises(ValueError):
            t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        self.assertFalse(mock_transform_source.called)
        shutil.rmtree(this_output_dir)

    @mock.patch('koza.cli_runner.transform_source')
    def test_hpa_transform(self, mock_transform_source):
        t = ProteinAtlasTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"hpa")
        with self.assertRaises(ValueError):
            t.run()
        self.assertTrue(os.path.exists(this_output_dir))
        self.assertFalse(mock_transform_source.called)
        shutil.rmtree(this_output_dir)
