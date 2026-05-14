import unittest
from pathlib import Path
from nttt.restore import restore_md
from nttt.strip import strip_md


class TestStripRestoreRoundtrip(unittest.TestCase):
    def assert_roundtrip_file(self, file_path):
        content = file_path.read_text(encoding="utf-8")
        self.assertEqual(restore_md(strip_md(content), content, str(file_path)), content)

    def test_labelled_accordions(self):
        data_folder = Path(__file__).resolve().parent / "data" / "markdown"
        self.assert_roundtrip_file(data_folder / "labelled_accordions.md")

    def test_nested_rfm_markers(self):
        data_folder = Path(__file__).resolve().parent / "data" / "markdown"
        self.assert_roundtrip_file(data_folder / "nested_modern_markers.md")

    def test_legacy_quiz_markers(self):
        data_folder = Path(__file__).resolve().parent / "data" / "markdown"
        self.assert_roundtrip_file(data_folder / "legacy_quiz_markers.md")


if __name__ == "__main__":
    unittest.main()
