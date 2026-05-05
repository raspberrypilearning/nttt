import io
import unittest
from unittest.mock import patch
from nttt.restore import restore_md


class TestRestore(unittest.TestCase):
    def test_restore_bare_marker(self):
        english = (
            "Intro\n"
            "> [!TASK]\n"
            ">\n"
            "> Do this.\n")
        translated = (
            "Intro translated\n"
            "> Do this translated.\n")
        expected = (
            "Intro translated\n"
            "> [!TASK]\n"
            ">\n"
            "> Do this translated.\n")

        self.assertEqual(restore_md(translated, english, "step_1.md"), expected)

    def test_restore_labelled_marker_preserves_translated_label(self):
        english = "> [!ACCORDION] Where are my voice recordings stored?\n>\n> Body\n"
        translated = "> Wo werden meine Sprachaufnahmen gespeichert?\n>\n> Inhalt\n"
        expected = "> [!ACCORDION] Wo werden meine Sprachaufnahmen gespeichert?\n>\n> Inhalt\n"

        self.assertEqual(restore_md(translated, english, "step_1.md"), expected)

    def test_restore_nested_labelled_marker(self):
        english = "> > [!ACCORDION] Teacher notes\n> >\n> > Body\n"
        translated = "> > Notizen fuer Lehrende\n> >\n> > Inhalt\n"
        expected = "> > [!ACCORDION] Notizen fuer Lehrende\n> >\n> > Inhalt\n"

        self.assertEqual(restore_md(translated, english, "step_1.md"), expected)

    def test_restore_warns_and_skips_on_count_mismatch(self):
        english = "> [!TASK]\n>\n> Do this.\n"
        translated = "> Do this.\n> Extra line.\n"

        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            result = restore_md(translated, english, "step_1.md")

        self.assertEqual(result, translated)
        self.assertIn("Different stripped structure", stderr.getvalue())

    def test_restore_noop_for_file_without_markers(self):
        english = "Intro\nBody\n"
        translated = "Intro translated\nBody translated\n"

        self.assertEqual(restore_md(translated, english, "step_1.md"), translated)


if __name__ == "__main__":
    unittest.main()
