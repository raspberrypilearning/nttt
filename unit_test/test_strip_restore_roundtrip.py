import unittest
from pathlib import Path
from nttt.restore import restore_md
from nttt.strip import strip_md


class TestStripRestoreRoundtrip(unittest.TestCase):
    def assert_roundtrip_file(self, file_path):
        content = file_path.read_text(encoding="utf-8")
        self.assertEqual(restore_md(strip_md(content), content, str(file_path)), content)

    def test_test_markdown_alien_step_with_labelled_accordions(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.assert_roundtrip_file(repo_root / "test-markdown-alien" / "en" / "step_1.md")

    def test_space_talk_step_with_nested_modern_markers(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.assert_roundtrip_file(repo_root / "space-talk" / "en" / "step_1.md")

    def test_space_talk_quiz_with_legacy_markers(self):
        repo_root = Path(__file__).resolve().parents[2]
        self.assert_roundtrip_file(repo_root / "space-talk" / "en" / "quiz1" / "question_1.md")


if __name__ == "__main__":
    unittest.main()
