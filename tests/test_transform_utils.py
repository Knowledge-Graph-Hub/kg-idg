import unittest
import os
from parameterized import parameterized
from kg_idg.utils.transform_utils import guess_bl_category, collapse_uniprot_curie
from kg_idg.transform_utils.orphanet.orphanet import OrphanetTransform
from kg_idg.transform_utils.omim.omim import OMIMTransform
from kg_idg.transform_utils.drug_central.drug_central import DrugCentralTransform

class TestTransformUtils(unittest.TestCase):

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
    def test_drug_central_transform(self):
        t = DrugCentralTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"drug_central")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))
    
    def test_orphanet_transform(self):
        t = OrphanetTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"orphanet")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))

    def test_omim_transform(self):
        t = OMIMTransform(self.input_dir,self.output_dir)
        this_output_dir = os.path.join(self.output_dir,"omim")
        t.run()
        self.assertTrue(os.path.exists(this_output_dir))

