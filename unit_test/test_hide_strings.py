import io
import unittest
from nttt import hide_strings


SAMPLE_LISTING = (
    "#101  Just some ordinary prose that should stay visible.\n"
    "#102  --- task ---\n"
    "#103  --- /no-print ---\n"
    "#104  > [!HINT]\n"
    "#105  > [!ACCORDION] Downloading the software\n"
    "#106  > [!ACCORDION]\n"
    "#107  hero_image images/cover.png\n"
    "#108  Another translatable sentence.\n"
)


class TestHideStrings(unittest.TestCase):

    def test_finds_legacy_rfm_and_raw(self):
        results = hide_strings.find_hidden_strings(SAMPLE_LISTING)
        ids = hide_strings.unique_ids(results)
        self.assertEqual(ids, ["102", "103", "104", "106", "107"])

    def test_does_not_match_prose(self):
        results = hide_strings.find_hidden_strings(SAMPLE_LISTING)
        ids = hide_strings.unique_ids(results)
        self.assertNotIn("101", ids)
        self.assertNotIn("108", ids)

    def test_does_not_hide_titled_rfm_alerts(self):
        results = hide_strings.find_hidden_strings(SAMPLE_LISTING)
        ids = hide_strings.unique_ids(results)
        self.assertNotIn("105", ids)

        titled_task = "#109  > [!TASK] With a title\n"
        results = hide_strings.find_hidden_strings(titled_task)
        self.assertEqual(hide_strings.unique_ids(results), [])

    def test_finds_titled_rfm_alerts_to_unhide(self):
        results = hide_strings.find_unhidden_strings(SAMPLE_LISTING)
        ids = hide_strings.unique_ids(results)
        self.assertEqual(ids, ["105"])

        titled_task = "#109  [!TASK] With a title\n"
        results = hide_strings.find_unhidden_strings(titled_task)
        self.assertEqual(hide_strings.unique_ids(results), ["109"])

    def test_does_not_unhide_titleless_rfm_alerts(self):
        titleless_task = "#109  [!TASK]\n"
        results = hide_strings.find_unhidden_strings(titleless_task)
        self.assertEqual(hide_strings.unique_ids(results), [])

    def test_records_matched_marker(self):
        results = hide_strings.find_hidden_strings(SAMPLE_LISTING)
        by_id = {r["id"]: r["marker"] for r in results}
        self.assertEqual(by_id["102"], "--- task ---")
        self.assertEqual(by_id["106"], "[!ACCORDION]")
        self.assertEqual(by_id["107"], "hero_image images/")

    def test_id_without_hash_prefix(self):
        results = hide_strings.find_hidden_strings("102\t--- task ---\n")
        self.assertEqual(hide_strings.unique_ids(results), ["102"])

    def test_finds_collapsed_markers_when_verbose_text_is_on_next_line(self):
        listing = (
            "#108\n"
            "Text: --- /task --- --- /no-print ---\n"
        )
        results = hide_strings.find_hidden_strings(listing)
        self.assertEqual(hide_strings.unique_ids(results), ["108"])

    def test_finds_close_markers_when_crowdin_escapes_slashes(self):
        listing = (
            "#109  --- \\/task --- --- \\/no-print ---\n"
        )
        results = hide_strings.find_hidden_strings(listing)
        self.assertEqual(hide_strings.unique_ids(results), ["109"])

    def test_finds_collapsed_close_markers_when_crowdin_escapes_markdown(self):
        listing = (
            "#110  \\--- \\/task \\--- \\--- \\/no-print \\---\n"
        )
        results = hide_strings.find_hidden_strings(listing)
        self.assertEqual(hide_strings.unique_ids(results), ["110"])

    def test_finds_crowdin_combined_marker_lines_after_labelled_id(self):
        listing = (
            "String ID: 111\n"
            "Text: --- /task --- --- /no-print ---\n"
        )
        results = hide_strings.find_hidden_strings(listing)
        self.assertEqual(hide_strings.unique_ids(results), ["111"])

    def test_finds_crowdin_combined_marker_lines_with_html_entities(self):
        listing = (
            "#112  --- &#x2F;task --- --- &#x2F;no-print ---\n"
        )
        results = hide_strings.find_hidden_strings(listing)
        self.assertEqual(hide_strings.unique_ids(results), ["112"])

    def test_unique_ids_dedupes(self):
        results = [{"id": "5"}, {"id": "5"}, {"id": "9"}]
        self.assertEqual(hide_strings.unique_ids(results), ["5", "9"])

    def test_run_prints_ids(self):
        out = io.StringIO()
        hide_strings.run(io.StringIO(SAMPLE_LISTING), out)
        self.assertEqual(out.getvalue().split(), ["102", "103", "104", "106", "107"])

    def test_run_prints_unhide_ids(self):
        out = io.StringIO()
        hide_strings.run(io.StringIO(SAMPLE_LISTING), out, unhide=True)
        self.assertEqual(out.getvalue().split(), ["105"])


if __name__ == '__main__':
    unittest.main()
