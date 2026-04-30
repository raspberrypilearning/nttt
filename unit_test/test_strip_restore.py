import unittest
from nttt import restore
from nttt import strip


class TestStripRestore(unittest.TestCase):
    def test_strip_md_replaces_non_translatable_markers(self):
        c_initial = ('--- task ---\n'
                     '\n'
                     'Complete this step.\n'
                     '\n'
                     '> [!HINT]\n'
                     '>\n'
                     '> Try this.\n'
                     '\n'
                     '```python filename="button.py"\n'
                     'print("Hello")\n'
                     '```\n'
                     '\n'
                     'The `Looks`{:class="block3looks"} category.\n'
                     '\n'
                     '--- /task ---')

        stripped, token_map = strip.strip_md(c_initial, "step_1.md")

        self.assertIn("<!-- NTTT:", stripped)
        self.assertNotIn("--- task ---", stripped)
        self.assertNotIn("[!HINT]", stripped)
        self.assertNotIn('filename="button.py"', stripped)
        self.assertNotIn('{:class="block3looks"}', stripped)
        self.assertEqual(len(token_map), 5)

    def test_restore_md_uses_english_to_regenerate_token_map(self):
        c_english = ('--- task ---\n'
                     '\n'
                     'Complete this step.\n'
                     '\n'
                     '> [!HINT]\n'
                     '>\n'
                     '> Try this.\n'
                     '\n'
                     '--- /task ---')
        stripped, _ = strip.strip_md(c_english, "step_1.md")
        translated = stripped.replace("Complete this step.", "Voltooi deze stap.")
        translated = translated.replace("Try this.", "Probeer dit.")

        c_target = ('--- task ---\n'
                    '\n'
                    'Voltooi deze stap.\n'
                    '\n'
                    '> [!HINT]\n'
                    '>\n'
                    '> Probeer dit.\n'
                    '\n'
                    '--- /task ---')

        self.assertEqual(restore.restore_md(translated, c_english, "step_1.md", "step_1.md"), c_target)

    def test_restore_md_leaves_unknown_placeholders(self):
        c_initial = "<!-- NTTT:abcdef-001 -->\nTranslated text."
        c_english = "English text."

        self.assertEqual(restore.restore_md(c_initial, c_english, "step_1.md", "step_1.md"), c_initial)

    def test_strip_restore_roundtrip_is_identity_for_english(self):
        c_english = ('> [!TASK]\n'
                     '>\n'
                     '> Complete this step.\n'
                     '\n'
                     '```python filename="button.py"\n'
                     'print("Hello")\n'
                     '```')
        stripped, _ = strip.strip_md(c_english, "step_1.md")

        self.assertEqual(restore.restore_md(stripped, c_english, "step_1.md", "step_1.md"), c_english)

    def test_strip_meta_yaml_removes_non_translatable_keys(self):
        c_initial = ('---\n'
                     'title: Test project\n'
                     'hero_image: images/banner.png\n'
                     'description: A project\n')

        stripped, _ = strip.strip_meta_yaml(c_initial, "meta.yml")

        self.assertIn("title: Test project", stripped)
        self.assertIn("description: A project", stripped)
        self.assertNotIn("hero_image", stripped)

    def test_restore_meta_yaml_merges_translated_keys_into_english(self):
        c_english = ('---\n'
                     'title: Test project\n'
                     'hero_image: images/banner.png\n'
                     'description: A project\n')
        c_translated = ('---\n'
                        'title: Testproject\n'
                        'description: Een project\n')

        restored = restore.restore_meta_yaml(c_translated, c_english)

        self.assertIn("title: Testproject", restored)
        self.assertIn("description: Een project", restored)
        self.assertIn("hero_image: images/banner.png", restored)


if __name__ == "__main__":
    unittest.main()
