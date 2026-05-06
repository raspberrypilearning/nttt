import unittest
from nttt import cleanup_sections
from nttt.restore import restore_md


class TestCleanupSections(unittest.TestCase):
    logging = "off"

    def test_remove_backslashes(self):
        c_initial = ("\\--- task \\---\n"
                     "\n"
                     "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                     "\n"
                     "\\--- /task \\---")

        c_target = ("--- task ---\n"
                    "\n"
                    "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                    "\n"
                    "--- /task ---")

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_missing_spaces(self):
        c_initial = ("\\---task \\---\n"
                     "\n"
                     "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                     "\n"                     
                     "\\--- /task\\---")

        c_target = ("--- task ---\n"
                    "\n"
                    "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                    "\n"                    
                    "--- /task ---")

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_double_dash(self):
        c_initial = ("--task --\n"
                     "\n"
                     "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                     "\n"                     
                     "-- /task\\---")

        c_target = ("--- task ---\n"
                    "\n"
                    "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                    "\n"
                    "--- /task ---")

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_hints(self):
        c_initial = ('\\--- hints \\--- \\--- hint \\---\n'
                     '\n'
                     'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                     '\n'
                     '\\--- /hint \\--- \\--- hint \\---\n'
                     '\n'
                     'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                     '\n'
                     '\\--- /hint \\--- \\--- hint \\---\n'
                     '\n'
                     'Dit is hoe je code eruit zou moeten zien:\n'
                     '\n'
                     '\\--- /hint \\--- \\--- /hints \\---')
        c_target = ('--- hints ---\n'
                    '--- hint ---\n'
                    '\n'
                    'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- hint ---\n'
                    '\n'
                    'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- hint ---\n'
                    '\n'
                    'Dit is hoe je code eruit zou moeten zien:\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- /hints ---')

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_hints2(self):
        c_initial = '\--- hints \--- \--- hint \--- ![screenshot](images/boat-levels-blocks.png) \--- /hint \--- \--- /hints \---'
        c_target = ('--- hints ---\n'
                    '--- hint ---\n'
                    '![screenshot](images/boat-levels-blocks.png)\n'
                    '--- /hint ---\n'
                    '--- /hints ---')

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_tables(self):
        """
        Verify that markdown tables are not modified
        """
        c_initial = ('| C  | D  | E  | F  | G  | A  | B  |\n'
                     '|:--:|:--:|:--:|:--:|:--:|:--:|:--:|\n'
                     '| 60 | 62 | 64 | 65 | 67 | 69 | 71 |')

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_initial)

    def test_tables2(self):
        """
        Verify that markdown tables are not modified
        """
        c_initial = ('| C (Do) | D (Re) | E (Mi) | F (Fa) | G (Sol) | A (La) | B (Si) |\n'
                     '|:------:|:------:|:------:|:------:|:-------:|:------:|:------:|\n'
                     '|   60   |   62   |   64   |   65   |   67    |   69   |   71   |')

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_initial)

    def test_fix_task(self):
        c_initial = ('\\--- task \\--- \\--- hints \\--- \\--- hint \\---\n'
                     '\\--- /hint \\--- \\--- /hints \\--- \\--- /task \\---')
        c_target = ('--- task ---\n'
                    '--- hints ---\n'
                    '--- hint ---\n'
                    '--- /hint ---\n'
                    '--- /hints ---\n'
                    '--- /task ---')

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_nested_feedback(self):
        c_initial = (
            '--- choices ---\n'
            '\n'
            '- ( ) Onmiddellijk zodra je op de groene vlag klikt\n'
            '\n'
            '  --- feedback ---\n'
            '\n'
            'De code heeft een klokblok voordat de bus wegglijdt.\n'
            '\n'
            '  --- /feedback ---\n'
            '\n'
            '--- /choices ---\n'
        )
        c_target = c_initial

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_title(self):
        c_initial = ('## \\--- collapse \\---\n'
                     '\n'
                     '## title: Нотатки керівника клубу\n'
                     '\n'
                     '## Вступ:\n')

        c_target = ('--- collapse ---\n'
                    '---\n'
                    'title: Нотатки керівника клубу\n'
                    '---\n'
                    '\n'
                    '## Вступ:\n')
        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_title_translated(self):
        c_initial = ('## \\--- collapse \\---\n'
                     '\n'
                     '## Назва: Нотатки керівника клубу\n'
                     '\n'
                     '## Вступ:\n')

        c_target = ('--- collapse ---\n'
                    '---\n'
                    'title: Нотатки керівника клубу\n'
                    '---\n'
                    '\n'
                    '## Вступ:\n')
        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_fix_translation_mismatch(self):
        c_initial = ('--- wenken ---\n'
                     '--- wenk ---\n'
                     '\n'
                     'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                     '\n'
                     '--- /hint ---\n'
                     '--- wenk ---\n'
                     '\n'
                     'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                     '\n'
                     '--- /wenk ---\n'
                     '--- hint ---\n'
                     '\n'
                     'Dit is hoe je code eruit zou moeten zien:\n'
                     '\n'
                     '--- /hint ---\n'
                     '--- /hints ---')
        c_original = ('--- hints ---\n'
                      '--- hint ---\n'
                      '\n'
                      'The boat should only point towards the mouse pointer and move `if`{:class="block3control"} the `distance to the mouse pointer`{:class="block3sensing"} is `greater than 5 pixels`{:class="block3operators"}.\n'
                      '\n'
                      '--- /hint ---\n'
                      '--- hint ---\n'
                      '\n'
                      'These are the code blocks you need to add to the code for the boat sprite:\n'
                      '\n'
                      '--- /hint ---\n'
                      '--- /hints ---')
        c_target = ('--- wenken ---\n'
                    '--- wenk ---\n'
                    '\n'
                    'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- wenk ---\n'
                    '\n'
                    'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                    '\n'
                    '--- /wenk ---\n'
                    '--- hint ---\n'
                    '\n'
                    'Dit is hoe je code eruit zou moeten zien:\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- /hints ---')

        self.assertEqual(cleanup_sections.revert_section_translation("step_1.md", c_initial, c_original, self.logging), c_target)

    def test_fix_translation_match(self):
        c_initial = ('--- wenken ---\n'
                     '--- wenk ---\n'
                     '\n'
                     'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                     '\n'
                     'Extra line\n'
                     '--- /hint ---\n'
                     '--- wenk ---\n'
                     '\n'
                     'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                     '\n'
                     '--- /wenk ---\n'
                     '--- hint ---\n'
                     '\n'
                     'Dit is hoe je code eruit zou moeten zien:\n'
                     '\n'
                     '--- /hint ---\n'
                     '--- /hints ---')
        c_original = ('--- hints ---\n'
                      '--- hint ---\n'
                      '\n'
                      'The boat should only point towards the mouse pointer and move `if`{:class="block3control"} the `distance to the mouse pointer`{:class="block3sensing"} is `greater than 5 pixels`{:class="block3operators"}.\n'
                      '\n'
                      '--- /hint ---\n'
                      '--- hint ---\n'
                      '\n'
                      'These are the code blocks you need to add to the code for the boat sprite:\n'
                      '\n'
                      '--- /hint ---\n'
                      '--- hint ---\n'
                      '\n'
                      'This is what your code should look like:\n'
                      '\n'
                      '--- /hint ---\n'
                      '--- /hints ---')
        c_target = ('--- hints ---\n'
                    '--- hint ---\n'
                    '\n'
                    'De boot mag alleen naar de muisaanwijzer wijzen en bewegen `als>`{:class="block3control"} de `afstand tot muisaanwijzer`{:class="block3sensing"} `groter dan 5 pixels`{:class="block3operators"} is.\n'
                    '\n'
                    'Extra line\n'
                    '--- /hint ---\n'
                    '--- hint ---\n'
                    '\n'
                    'Dit zijn de code blokken die je moet toevoegen aan de code voor de boot-sprite:\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- hint ---\n'
                    '\n'
                    'Dit is hoe je code eruit zou moeten zien:\n'
                    '\n'
                    '--- /hint ---\n'
                    '--- /hints ---')

        self.assertEqual(cleanup_sections.revert_section_translation("step_1.md", c_initial, c_original, self.logging), c_target)

    def test_fix_space_after_slash(self):
        c_initial = ("\\--- task \\---\n"
                     "\n"
                     "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                     "\n"
                     "\\--- /  task \\---")

        c_target = ("--- task ---\n"
                    "\n"
                    "Wat gebeurt er als de boot de muisaanwijzer bereikt? Probeer het uit om te zien wat het probleem is.\n"
                    "\n"
                    "--- /task ---")

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_tag_with_dash(self):
        c_initial = (r"\--- print-only \--- ![screenshot of finished game](images/memory-screenshot.png) \--- /print-only \---")

        c_target = ("--- print-only ---\n"
                    "![screenshot of finished game](images/memory-screenshot.png)\n"
                    "--- /print-only ---")

        self.assertEqual(cleanup_sections.fix_sections(c_initial, self.logging), c_target)

    def test_no_collapse_doubling_for_crowdin_broken_with_matching_line_count(self):
        """
        Regression for the user-reported bug: in default `tidy` mode, when a
        Crowdin-broken locale file happens to have the same line count as the
        stripped English reference, `restore_md` would insert legacy bare
        markers from English while `fix_sections` separately rebuilt them from
        the `## --- collapse ---` / `## title:` Crowdin pattern, producing
        duplicated `--- collapse ---` and `--- /collapse ---` lines.

        The pipeline (restore_md -> fix_sections) must produce a single,
        canonical `--- collapse ---` block.
        """
        en = ("## What you will make\n"
              "\n"
              "Use the face recognition tools.\n"
              "\n"
              "You will need a **webcam**.\n"
              "\n"
              "![Image.](images/foo.png)\n"
              "\n"
              "--- collapse ---\n"
              "---\n"
              "title: Where are my images stored?\n"
              "---\n"
              "\n"
              "- This project uses a technology.\n"
              "- No images from your webcam.\n"
              "\n"
              "--- /collapse ---\n"
              "\n"
              "\n"
              "--- collapse ---\n"
              "---\n"
              "title: No YouTube?\n"
              "---\n"
              "\n"
              "You can [download].\n"
              "\n"
              "\n"
              "--- /collapse ---\n")

        fr = ("## Ce que tu vas faire\n"
              "\n"
              "Utilise les outils.\n"
              "\n"
              "Tu auras besoin d'une **webcam**.\n"
              "\n"
              "![Image.](images/foo.png)\n"
              "\n"
              "## \\--- collapse \\---\n"
              "\n"
              "## title: Ou sont stockees mes images ?\n"
              "\n"
              "- Ce projet.\n"
              "- Aucune image.\n"
              "\n"
              "\\--- /collapse \\---\n"
              "\n"
              "## \\--- collapse \\---\n"
              "\n"
              "## title: Pas de YouTube ?\n"
              "\n"
              "Tu peux [telecharger].\n"
              "\n"
              "\\--- /collapse \\---\n")

        # Mimic the default tidy pipeline: restore first, then fix_sections.
        restored = restore_md(fr, en, "step_1.md")
        fixed = cleanup_sections.fix_sections(restored, self.logging)

        # No duplicate markers anywhere.
        self.assertNotIn("--- collapse ---\n--- collapse ---", fixed)
        self.assertNotIn("--- /collapse ---\n--- /collapse ---", fixed)

        # Exactly two opening and two closing canonical legacy markers (one per
        # collapse block, and no Crowdin-broken `## ---` patterns left over).
        opening_lines = [line for line in fixed.splitlines() if line == "--- collapse ---"]
        closing_lines = [line for line in fixed.splitlines() if line == "--- /collapse ---"]
        self.assertEqual(len(opening_lines), 2)
        self.assertEqual(len(closing_lines), 2)
        self.assertNotIn("## ---", fixed)
        self.assertNotIn("\\---", fixed)

        # And the title blocks were rebuilt in canonical YAML form.
        self.assertIn("--- collapse ---\n"
                      "---\n"
                      "title: Ou sont stockees mes images ?\n"
                      "---\n", fixed)
        self.assertIn("--- collapse ---\n"
                      "---\n"
                      "title: Pas de YouTube ?\n"
                      "---\n", fixed)


if __name__ == '__main__':
    unittest.main()
