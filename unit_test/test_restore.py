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

    def test_restore_skips_when_translated_has_crowdin_escape(self):
        # Pure-stripped output never contains `\---`. If it is present, the
        # translated file is in Crowdin-mangled form and `fix_sections` will
        # handle it; restoration must not run, otherwise it would duplicate the
        # legacy bare markers from English.
        english = (
            "Intro\n"
            "--- collapse ---\n"
            "Body\n"
            "--- /collapse ---\n")
        translated = (
            "Intro translated\n"
            "\\--- collapse \\---\n"
            "Body translated\n"
            "\\--- /collapse \\---\n")

        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            result = restore_md(translated, english, "step_1.md")

        self.assertEqual(result, translated)
        self.assertEqual(stderr.getvalue(), "")

    def test_restore_skips_when_translated_has_heading_jammed_marker(self):
        # `## --- collapse ---` is a Crowdin-broken heading-jammed marker.
        # `fix_sections` rebuilds the canonical block; restoration must not run.
        english = (
            "## Heading\n"
            "\n"
            "--- collapse ---\n"
            "---\n"
            "title: Notes\n"
            "---\n"
            "\n"
            "Body\n"
            "\n"
            "--- /collapse ---\n")
        translated = (
            "## Heading translated\n"
            "\n"
            "## --- collapse ---\n"
            "\n"
            "## title: Notes translated\n"
            "\n"
            "Body translated\n"
            "\n"
            "--- /collapse ---\n")

        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            result = restore_md(translated, english, "step_1.md")

        self.assertEqual(result, translated)
        self.assertEqual(stderr.getvalue(), "")

    def test_restore_skips_when_translated_already_has_legacy_marker(self):
        # If the translated file already has canonical `--- collapse ---`
        # markers, restoration would duplicate them.
        english = (
            "Intro\n"
            "--- collapse ---\n"
            "Body\n"
            "--- /collapse ---\n")
        translated = (
            "Intro translated\n"
            "--- collapse ---\n"
            "Body translated\n"
            "--- /collapse ---\n")

        with patch("sys.stderr", new_callable=io.StringIO) as stderr:
            result = restore_md(translated, english, "step_1.md")

        self.assertEqual(result, translated)
        self.assertEqual(stderr.getvalue(), "")

    def test_restore_still_inserts_when_pure_stripped(self):
        # Regression: a pure-stripped translated file (no `\---`, no `## ---`,
        # no canonical legacy markers) must still get its markers restored.
        english = (
            "Intro\n"
            "--- collapse ---\n"
            "Body\n"
            "--- /collapse ---\n")
        translated = (
            "Intro translated\n"
            "Body translated\n")
        expected = (
            "Intro translated\n"
            "--- collapse ---\n"
            "Body translated\n"
            "--- /collapse ---\n")

        self.assertEqual(restore_md(translated, english, "step_1.md"), expected)


if __name__ == "__main__":
    unittest.main()
