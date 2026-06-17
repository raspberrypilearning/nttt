import unittest
from nttt import markers


class TestMarkers(unittest.TestCase):

    def test_loads_default_registry(self):
        registry = markers.load_markers()
        self.assertIn("markers", registry)
        self.assertIn("raw_patterns", registry)
        self.assertTrue(len(registry["markers"]) > 0)

    def test_hideable_strings_cover_both_syntaxes(self):
        strings = markers.hideable_strings()
        # legacy
        self.assertIn("--- task ---", strings)
        self.assertIn("--- /task ---", strings)
        self.assertIn("--- no-print ---", strings)
        # rfm
        self.assertIn("[!TASK]", strings)
        self.assertIn("[!HINT]", strings)
        self.assertIn("[!ACCORDION]", strings)
        # raw pattern
        self.assertIn("hero_image images/", strings)

    def test_hideable_strings_are_unique(self):
        strings = markers.hideable_strings()
        self.assertEqual(len(strings), len(set(strings)))

    def test_hide_false_is_excluded(self):
        registry = {
            "markers": [
                {"name": "shown", "hide": False, "rfm": {"alert": "[!SHOWN]"}},
                {"name": "hidden", "hide": True, "rfm": {"alert": "[!HIDDEN]"}},
            ],
            "raw_patterns": [],
        }
        strings = markers.hideable_strings(registry)
        self.assertIn("[!HIDDEN]", strings)
        self.assertNotIn("[!SHOWN]", strings)

    def test_alert_keywords(self):
        keywords = markers.alert_keywords()
        self.assertIn("TASK", keywords)
        self.assertIn("ACCORDION", keywords)
        self.assertNotIn("QUIZ", keywords)  # legacy-only, no RFM alert

    def test_legacy_tag_names(self):
        names = markers.legacy_tag_names()
        self.assertIn("task", names)
        self.assertIn("no-print", names)
        self.assertNotIn("info", names)  # RFM-only, no legacy marker


if __name__ == '__main__':
    unittest.main()
