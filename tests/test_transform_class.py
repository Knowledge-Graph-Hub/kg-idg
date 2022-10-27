import os
import tempfile
from unittest import TestCase

from parameterized import parameterized

from kg_idg.transform import DATA_SOURCES
from kg_idg.transform_utils.transform import Transform


class TestTransform(TestCase):
    def setUp(self) -> None:
        self.transform_instance = TransformChildClass()

    def test_reality(self):
        self.assertEqual(1, 1)

    @parameterized.expand(
        [
            ("source_name", "test_transform"),
            ("node_header", ["id", "name", "category"]),
            ("edge_header", ["subject", "edge_label", "object", "relation", "provided_by"]),
            ("output_base_dir", os.path.join("data", "transformed")),
            ("input_base_dir", os.path.join("data", "raw")),
            ("output_dir", os.path.join("data", "transformed", "test_transform")),
            (
                "output_node_file",
                os.path.join("data", "transformed", "test_transform", "nodes.tsv"),
            ),
            (
                "output_edge_file",
                os.path.join("data", "transformed", "test_transform", "edges.tsv"),
            ),
            (
                "output_json_file",
                os.path.join("data", "transformed", "test_transform", "nodes_edges.json"),
            ),
        ]
    )
    def test_attributes(self, attr, default):
        self.assertTrue(hasattr(self.transform_instance, attr))
        self.assertEqual(getattr(self.transform_instance, attr), default)

    @parameterized.expand(
        [("DEFAULT_INPUT_DIR", "data/raw"), ("DEFAULT_OUTPUT_DIR", "data/transformed")]
    )
    def test_default_dir(self, dir_var_name, dir_var_value):
        self.assertEqual(getattr(Transform, dir_var_name), dir_var_value)

    @parameterized.expand(
        list(DATA_SOURCES.keys()),
    )
    def test_transform_child_classes(self, src_name):
        """
        Make sure Transform child classes:
        - properly set default input_dir and output_dir
        - properly pass and set input_dir and output from constructor
        - implement run()

        :param src_name:
        :return: None
        """
        input_dir = os.path.join("tests", "resources")
        output_dir = os.path.join("output")
        def_input_dir = os.path.join("data", "raw")
        def_output_dir = os.path.join("data", "transformed")

        t = DATA_SOURCES[src_name](input_dir=input_dir, output_dir=output_dir)
        self.assertEqual(t.input_base_dir, input_dir)
        self.assertEqual(t.output_base_dir, output_dir)
        self.assertTrue(hasattr(t, "run"))
        self.assertEqual(t.DEFAULT_INPUT_DIR, def_input_dir)
        self.assertEqual(t.DEFAULT_OUTPUT_DIR, def_output_dir)

    def test_passthrough(self):
        tempdir = tempfile.mkdtemp()
        transform_name = "test"
        t = Transform(source_name=transform_name, output_dir=tempdir)
        self.assertTrue(hasattr(t, "pass_through"))

        edges_file = "tests/resources/dc_edges_snippet.tsv"
        nodes_file = "tests/resources/dc_nodes_snippet.tsv"
        t.pass_through(edges_file=edges_file, nodes_file=nodes_file)
        for f in [edges_file, nodes_file]:
            self.assertTrue(
                os.path.exists(os.path.join(tempdir, transform_name, os.path.basename(f)))
            )


class TransformChildClass(Transform):
    def __init__(self):
        super().__init__(source_name="test_transform")
