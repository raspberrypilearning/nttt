"""
Local round-trip fixtures for inspecting the hide + restore flows by eye.

Like test_fixtures.py, these write their results under test/fixtures/.../output/
(gitignored) so a maintainer can open the before/after files. They are NOT part
of the CI unit-test run; run them locally:

Normal run (assertions enabled):
    python -m unittest discover -s test -p "test_roundtrip.py" -v

Inspect mode (writes outputs, skips assertions):
    NTTT_INSPECT=1 python -m unittest discover -s test -p "test_roundtrip.py" -v

Hide flow   - test/fixtures/hide/:    a captured `crowdin string list` -> the IDs to hide.
Restore flow - test/fixtures/restore/: a mangled translation + English template -> restored file.
"""
import os
import unittest

import nttt.tidyup
from nttt import hide_strings

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
INSPECT = os.environ.get('NTTT_INSPECT') == '1'

HIDE = os.path.join(FIXTURES, 'hide')
RESTORE = os.path.join(FIXTURES, 'restore')


class TestHideFlow(unittest.TestCase):
    """Given a Crowdin listing, check which string IDs NTTT would hide."""

    def setUp(self):
        os.makedirs(os.path.join(HIDE, 'output'), exist_ok=True)

    def test_hide_list(self):
        listing_path = os.path.join(HIDE, 'input', 'crowdin_string_list.txt')
        with open(listing_path, encoding='utf-8') as f:
            listing = f.read()

        results = hide_strings.find_hidden_strings(listing)
        ids = hide_strings.unique_ids(results)

        # Write the IDs and a human-readable report for inspection.
        with open(os.path.join(HIDE, 'output', 'ids.txt'), 'w', encoding='utf-8') as f:
            f.write("\n".join(ids) + "\n")
        with open(os.path.join(HIDE, 'output', 'report.txt'), 'w', encoding='utf-8') as f:
            f.write(hide_strings.format_report(results) + "\n")

        if not INSPECT:
            # markers (legacy + title-less RFM + raw) are hidden ...
            for expected in ['5002', '5004', '5005', '5007', '5008', '5011', '5012']:
                self.assertIn(expected, ids)
            # ... plain prose and titled RFM alerts are not.
            for prose in ['5001', '5003', '5006', '5009', '5010', '5013']:
                self.assertNotIn(prose, ids)

        print(f'\n  Output: {os.path.join(HIDE, "output", "ids.txt")}')


class TestRestoreFlow(unittest.TestCase):
    """Given a mangled translation + the English template, check the restored file."""

    def setUp(self):
        os.makedirs(os.path.join(RESTORE, 'output'), exist_ok=True)

    def test_restore_step_7(self):
        src = os.path.join(RESTORE, 'input', 'step_7.md')
        en = os.path.join(RESTORE, 'en', 'step_7.md')
        dst = os.path.join(RESTORE, 'output', 'step_7.md')

        nttt.tidyup.fix_md_step(src, 'es', en, dst, (), 'off')

        with open(dst, encoding='utf-8') as f:
            result = f.read()

        if not INSPECT:
            with open(os.path.join(RESTORE, 'expected', 'step_7.md'), encoding='utf-8') as f:
                expected = f.read()
            self.assertEqual(result, expected)

        print(f'\n  Output: {dst}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
