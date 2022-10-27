from unittest import TestCase

from click.testing import CliRunner

from kg_idg.transform_utils.ontology.ontology_transform import ONTOLOGIES
from run import download, merge, transform


class TestRun(TestCase):
    """Tests the run.py script."""

    def setUp(self) -> None:
        self.runner = CliRunner()

    def test_download(self):
        # Test correct download
        result = self.runner.invoke(cli=download, args=["-y", "tests/resources/download.yaml"])
        self.assertRegex(result.output, "Downloading")

        # Test if download.yaml not found
        result = self.runner.invoke(cli=download, args=["-y", "tests/resources/zownload.yam"])
        self.assertRegex(result.output, "Error")

    def test_transform(self):
        # Test full transform with ontologies only
        for source in ONTOLOGIES:
            result = self.runner.invoke(
                cli=transform, args=["-i", "tests/resources/snippets/", "-s", source]
            )
            self.assertEqual(result.exit_code, 0)
        # Test if raw transform input not available
        result = self.runner.invoke(cli=transform, args=["-i", "tests/data/rawr"])
        self.assertNotEqual(result.exit_code, 0)

    def test_merge_missing_file_error(self):
        with self.assertRaises(FileNotFoundError):
            result = self.runner.invoke(
                catch_exceptions=False,
                cli=merge,
                args=["-y", "tests/resources/merge_MISSING_FILE.yaml"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertRegexpMatches(result.output, "does not exist")
