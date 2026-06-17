import unittest
from nttt import cleanup_alerts


class TestCleanupAlerts(unittest.TestCase):
    logging = "off"

    def _fix(self, content):
        return cleanup_alerts.fix_alerts(content, self.logging)

    def test_adds_missing_space_after_gt(self):
        self.assertEqual(self._fix(">[!TASK]"), "> [!TASK]")

    def test_strips_spaces_inside_brackets(self):
        self.assertEqual(self._fix("> [! TASK ]"), "> [!TASK]")

    def test_uppercases_keyword(self):
        self.assertEqual(self._fix("> [!task]"), "> [!TASK]")

    def test_unescapes_crowdin_backslash(self):
        self.assertEqual(self._fix("> \\[!HINT]"), "> [!HINT]")

    def test_preserves_accordion_title(self):
        self.assertEqual(
            self._fix("> [!ACCORDION]   Downloading the software  "),
            "> [!ACCORDION] Downloading the software",
        )

    def test_nested_blockquote_levels(self):
        self.assertEqual(self._fix("> >[!hint]"), "> > [!HINT]")

    def test_leaves_normal_blockquote_untouched(self):
        content = "> Just a quote, not an alert.\n> Another line."
        self.assertEqual(self._fix(content), content)

    def test_multiline_block(self):
        content = ">[!TASK]\n>\n> Do the thing.\n"
        expected = "> [!TASK]\n>\n> Do the thing.\n"
        self.assertEqual(self._fix(content), expected)

    def test_revert_translated_keyword(self):
        translated = "> [!TAREA]\n>\n> Hazlo.\n"
        english = "> [!TASK]\n>\n> Do it.\n"
        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step.md", translated, english, self.logging),
            "> [!TASK]\n>\n> Hazlo.\n",
        )

    def test_revert_preserves_translated_accordion_title(self):
        translated = "> [!ACORDEON] Titulo traducido\n"
        english = "> [!ACCORDION] English title\n"
        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step.md", translated, english, self.logging),
            "> [!ACCORDION] Titulo traducido\n",
        )

    def test_revert_skips_on_count_mismatch(self):
        translated = "> [!TAREA]\n> [!PISTA]\n"
        english = "> [!TASK]\n"
        # counts differ -> content returned unchanged
        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step.md", translated, english, self.logging),
            translated,
        )

    def test_revert_handles_mixed_with_legacy(self):
        # legacy "--- task ---" lines are not alert headers and must be ignored here
        translated = "--- taak ---\n> [!PISTA]\n"
        english = "--- task ---\n> [!HINT]\n"
        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step.md", translated, english, self.logging),
            "--- taak ---\n> [!HINT]\n",
        )


if __name__ == '__main__':
    unittest.main()
