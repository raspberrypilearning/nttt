import unittest
from nttt.markers import (
    LINE_KIND_BARE_MARKER,
    LINE_KIND_LABELLED_MARKER,
    LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE,
    LINE_KIND_REGULAR,
    classify_line,
    iter_lines_with_fence_state,
    is_marker_line,
    is_paired_empty_blockquote,
)


class TestMarkers(unittest.TestCase):
    def assert_line_kind(self, line, expected_kind):
        line_kind, _ = classify_line(line)
        self.assertEqual(line_kind, expected_kind)

    def test_bare_rfm_markers(self):
        self.assert_line_kind("> [!TASK]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> [!NOPRINT]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> [!PRINTONLY]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> [!HINT]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> [!CHALLENGE]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> [!SAVE]", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("> > [!TASK]", LINE_KIND_BARE_MARKER)

    def test_labelled_rfm_markers(self):
        line_kind, match = classify_line("> [!ACCORDION] Where are my voice recordings stored?")
        self.assertEqual(line_kind, LINE_KIND_LABELLED_MARKER)
        self.assertEqual(match.group("tag"), "ACCORDION")
        self.assertEqual(match.group("label"), "Where are my voice recordings stored?")

    def test_empty_blockquote(self):
        self.assert_line_kind(">", LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE)
        self.assert_line_kind("> >", LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE)
        self.assertTrue(is_paired_empty_blockquote(">"))

    def test_bare_legacy_markers(self):
        self.assert_line_kind("--- task ---", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("--- /task ---", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("  --- feedback ---", LINE_KIND_BARE_MARKER)
        self.assert_line_kind("--- print-only ---", LINE_KIND_BARE_MARKER)

    def test_negative_cases(self):
        self.assert_line_kind("This paragraph contains --- task --- text.", LINE_KIND_REGULAR)
        self.assert_line_kind("\\--- task \\---", LINE_KIND_REGULAR)
        self.assert_line_kind("> Quote text", LINE_KIND_REGULAR)
        self.assertFalse(is_marker_line("> Quote text"))

    def test_iter_lines_with_fence_state_handles_two_fences_on_one_line(self):
        content = (
            "```inline```\n"
            "> [!TASK]\n"
            ">\n"
            "> Body\n")

        line_states = list(iter_lines_with_fence_state(content))

        self.assertEqual(
            line_states,
            [
                ("```inline```\n", False),
                ("> [!TASK]\n", False),
                (">\n", False),
                ("> Body\n", False),
            ])

    def test_iter_lines_with_fence_state_ignores_inline_triple_backticks(self):
        content = (
            "Text with ` ``` ` inline\n"
            "> [!TASK]\n"
            ">\n"
            "> Body\n")

        line_states = list(iter_lines_with_fence_state(content))

        self.assertEqual(
            line_states,
            [
                ("Text with ` ``` ` inline\n", False),
                ("> [!TASK]\n", False),
                (">\n", False),
                ("> Body\n", False),
            ])

    def test_iter_lines_with_fence_state_ignores_inline_triple_backticks_without_spaces(self):
        content = (
            "Text with ```inline``` marker\n"
            "> [!TASK]\n"
            ">\n"
            "> Body\n")

        line_states = list(iter_lines_with_fence_state(content))

        self.assertEqual(
            line_states,
            [
                ("Text with ```inline``` marker\n", False),
                ("> [!TASK]\n", False),
                (">\n", False),
                ("> Body\n", False),
            ])

    def test_iter_lines_with_fence_state_handles_language_fence_open_and_close(self):
        content = (
            "```python\n"
            "> [!TASK]\n"
            "```\n"
            "> Body\n")

        line_states = list(iter_lines_with_fence_state(content))

        self.assertEqual(
            line_states,
            [
                ("```python\n", False),
                ("> [!TASK]\n", True),
                ("```\n", True),
                ("> Body\n", False),
            ])


if __name__ == "__main__":
    unittest.main()
