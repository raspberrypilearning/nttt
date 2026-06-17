"""
Integration fixture tests for NTTT.

Each test processes a real .md fixture file through fix_md_step and writes the
output to test/fixtures/output/ — open those files to inspect the before/after.

Normal run (assertions enabled):
    python -m unittest discover -s test -p "test_fixtures.py" -v

Inspect mode (writes outputs, skips assertions — useful when adding new
transformations and you want to see the raw output before writing assertions):
    NTTT_INSPECT=1 python -m unittest discover -s test -p "test_fixtures.py" -v
"""
import os
import unittest
import nttt.tidyup

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
INPUT = os.path.join(FIXTURES, 'input')
EN = os.path.join(FIXTURES, 'en')
OUTPUT = os.path.join(FIXTURES, 'output')

INSPECT = os.environ.get('NTTT_INSPECT') == '1'


class TestFixtures(unittest.TestCase):

    def setUp(self):
        os.makedirs(OUTPUT, exist_ok=True)

    def _assertIn(self, member, container):
        if not INSPECT:
            super().assertIn(member, container)

    def _assertNotIn(self, member, container):
        if not INSPECT:
            super().assertNotIn(member, container)

    def _run(self, step, lang='nl'):
        src = os.path.join(INPUT, step)
        en_src = os.path.join(EN, step)
        dst = os.path.join(OUTPUT, step)
        nttt.tidyup.fix_md_step(src, lang, en_src, dst, (), 'off')
        with open(dst, encoding='utf-8') as f:
            return f.read()

    def test_step_1_section_markers(self):
        """
        Verifies that backslash-escaped section markers are normalised and
        translated section tag names are reverted to their English equivalents.

        Input:  \\--- taak \\--- \\--- tips \\--- \\--- tip \\---  (jammed, escaped)
        Output: --- task ---  /  --- hints ---  /  --- hint ---  (split, English)
        """
        result = self._run('step_1.md')

        self._assertIn('--- task ---', result)
        self._assertIn('--- hints ---', result)
        self._assertIn('--- hint ---', result)
        self._assertIn('--- /hint ---', result)
        self._assertIn('--- /hints ---', result)
        self._assertIn('--- /task ---', result)

        self._assertNotIn('\\---', result)
        self._assertNotIn('--- taak ---', result)
        self._assertNotIn('--- tips ---', result)
        self._assertNotIn('--- tip ---', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_1.md")}')

    def test_step_2_markdown_delimiters(self):
        """
        Verifies that extra whitespace inside markdown emphasis delimiters is
        stripped, while code-block content is left untouched.

        Input:  _ groene vlag _  /  ** zeven **  /  ` je naam `
        Output: _groene vlag_    /  **zeven**     /  `je naam`
        Code block interior (3 * 2 * 1) preserved unchanged.
        """
        result = self._run('step_2.md')

        self._assertIn('_groene vlag_', result)
        self._assertIn('**zeven**', result)
        self._assertIn('`je naam`', result)

        self._assertNotIn('_ groene vlag _', result)
        self._assertNotIn('** zeven **', result)
        self._assertNotIn('` je naam `', result)

        self._assertIn('3 * 2 * 1', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_2.md")}')

    def test_step_3_html_tags(self):
        """
        Verifies that padding inside simple inline HTML tags is stripped, while
        content wrapped in backtick spans is left untouched.

        Input:  <kbd> Enter </kbd>  /  <strong> OK </strong>
        Output: <kbd>Enter</kbd>    /  <strong>OK</strong>
        Backtick span `<code> ongekruist </code>` preserved unchanged.
        """
        result = self._run('step_3.md')

        self._assertIn('<kbd>Enter</kbd>', result)
        self._assertIn('<strong>OK</strong>', result)

        self._assertNotIn('<kbd> Enter </kbd>', result)
        self._assertNotIn('<strong> OK </strong>', result)

        self._assertIn('`<code> ongekruist </code>`', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_3.md")}')

    def test_step_4_formatting_braces(self):
        """
        Verifies that { :class = "..." } attribute blocks are normalised:
        extra spaces removed, attribute name and value lowercased, and the
        _blank target shorthand fixed.

        Input:  { : class = "block3control"}  /  {: CLASS = "block3sensing" }  /  {:target=" _ blank"}
        Output: {:class="block3control"}       /  {:class="block3sensing"}       /  {:target="_blank"}
        """
        result = self._run('step_4.md')

        self._assertIn('{:class="block3control"}', result)
        self._assertIn('{:class="block3sensing"}', result)
        self._assertIn('{:target="_blank"}', result)

        self._assertNotIn('{ : class', result)
        self._assertNotIn('CLASS', result)
        self._assertNotIn('" _ blank"', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_4.md")}')

    def test_step_5_url_rewrite(self):
        """
        Verifies that every /en/ path segment in the file is rewritten to the
        target language code.

        Input (lang=nl):  /en/projects/boat-race  /  /en/projects/another-project/step_1
        Output:           /nl/projects/boat-race  /  /nl/projects/another-project/step_1
        """
        result = self._run('step_5.md', lang='nl')

        self._assertIn('/nl/projects/boat-race', result)
        self._assertIn('/nl/projects/another-project', result)

        self._assertNotIn('/en/projects/', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_5.md")}')

    def test_step_6_combined(self):
        """
        Verifies that all transformations work together on a single file:
        section markers fixed and reverted, markdown delimiters trimmed,
        HTML tags trimmed, formatting braces normalised, and URLs rewritten.
        """
        result = self._run('step_6.md', lang='nl')

        self._assertIn('--- task ---', result)
        self._assertIn('--- hint ---', result)
        self._assertNotIn('--- taak ---', result)
        self._assertNotIn('\\---', result)

        self._assertIn('_starten_', result)
        self._assertNotIn('_ starten _', result)

        self._assertIn('<kbd>Enter</kbd>', result)
        self._assertNotIn('<kbd> Enter </kbd>', result)

        self._assertIn('{:class="block3control"}', result)
        self._assertNotIn('{ : class', result)

        self._assertIn('/nl/projects/', result)
        self._assertNotIn('/en/projects/', result)

        print(f'\n  Output: {os.path.join(OUTPUT, "step_6.md")}')


if __name__ == '__main__':
    unittest.main(verbosity=2)
