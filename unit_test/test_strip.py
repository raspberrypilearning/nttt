import unittest
from nttt.strip import strip_md


class TestStrip(unittest.TestCase):
    def test_strip_bare_rfm_marker_and_paired_empty_blockquote(self):
        content = (
            "Intro\n"
            "> [!TASK]\n"
            ">\n"
            "> Do this.\n")

        expected = (
            "Intro\n"
            "> Do this.\n")

        self.assertEqual(strip_md(content), expected)

    def test_strip_labelled_rfm_marker_keeps_label(self):
        content = "> [!ACCORDION] Where are my voice recordings stored?\n>\n> Body\n"
        expected = "> Where are my voice recordings stored?\n>\n> Body\n"

        self.assertEqual(strip_md(content), expected)

    def test_strip_nested_blockquote_marker(self):
        content = (
            "> [!NOPRINT]\n"
            ">\n"
            "> > [!TASK]\n"
            "> >\n"
            "> > ### Play\n")

        expected = (
            "> > ### Play\n")

        self.assertEqual(strip_md(content), expected)

    def test_strip_legacy_marker(self):
        content = "--- task ---\nDo this.\n--- /task ---\n"
        expected = "Do this.\n"

        self.assertEqual(strip_md(content), expected)

    def test_preserve_code_fences(self):
        content = (
            "Before\n"
            "```\n"
            "> [!TASK]\n"
            "--- task ---\n"
            "```\n"
            "> [!SAVE]\n"
            ">\n"
            "After\n")

        expected = (
            "Before\n"
            "```\n"
            "> [!TASK]\n"
            "--- task ---\n"
            "```\n"
            "After\n")

        self.assertEqual(strip_md(content), expected)


if __name__ == "__main__":
    unittest.main()
