from unittest import TestCase


class TestDownload(TestCase):
    """Tests download"""

    def setUp(self) -> None:
        pass

    # @mock.patch('requests.get')
    # def test_download(self, mock_get):
    #     dl_file = 'data/raw/test_1234.pdf'
    #     if os.path.exists(dl_file):
    #         os.unlink(dl_file)
    #     tmpdir = tempfile.mkdtemp()
    #     download(yaml_file='tests/resources/download.yaml', output_dir=tmpdir)
    #     self.assertTrue(mock_get.called)
