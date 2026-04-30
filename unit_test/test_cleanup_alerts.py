import unittest
from nttt import cleanup_alerts


class TestCleanupAlerts(unittest.TestCase):
    logging = "off"

    def test_fix_alert_spacing_and_case(self):
        c_initial = ">[ ! task ] Complete this step."
        c_target = "> [!TASK] Complete this step."

        self.assertEqual(cleanup_alerts.fix_alerts(c_initial, self.logging), c_target)

    def test_fix_nested_alert(self):
        c_initial = "> >[!hint]\n> >\n> > Try this."
        c_target = "> > [!HINT]\n> >\n> > Try this."

        self.assertEqual(cleanup_alerts.fix_alerts(c_initial, self.logging), c_target)

    def test_revert_alert_translation_preserves_title(self):
        c_initial = "> [!TAAK] Uitdaging: Verbeter je drum"
        c_english = "> [!CHALLENGE] Challenge: Improving your drum"
        c_target = "> [!CHALLENGE] Uitdaging: Verbeter je drum"

        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step_1.md", c_initial, c_english, self.logging),
            c_target)

    def test_revert_alert_translation_skips_when_structure_differs(self):
        c_initial = "> [!TAAK]\n\n> [!HINT]"
        c_english = "> [!TASK]"

        self.assertEqual(
            cleanup_alerts.revert_alert_translation("step_1.md", c_initial, c_english, self.logging),
            c_initial)


if __name__ == "__main__":
    unittest.main()
