import unittest
from nttt import cleanup_codeblocks


class TestCleanupCodeblocks(unittest.TestCase):
    logging = "off"

    def test_fix_codeblock_info_string(self):
        c_initial = ('```Python filename = "Button_Press.py" line_numbers = "TRUE" line_highlights = "3, 5-6"\n'
                     'print("Hello")\n'
                     '```')
        c_target = ('```python filename="button_press.py" line_numbers="true" line_highlights="3,5-6"\n'
                    'print("Hello")\n'
                    '```')

        self.assertEqual(cleanup_codeblocks.fix_codeblocks(c_initial, None, self.logging), c_target)

    def test_fix_codeblock_uses_english_language_for_unknown_translated_language(self):
        c_initial = ('```pythone filename="button.py"\n'
                     'print("Hello")\n'
                     '```')
        c_english = ('```python filename="button.py"\n'
                     'print("Hello")\n'
                     '```')
        c_target = ('```python filename="button.py"\n'
                    'print("Hello")\n'
                    '```')

        self.assertEqual(cleanup_codeblocks.fix_codeblocks(c_initial, c_english, self.logging), c_target)

    def test_does_not_change_plain_fences(self):
        c_initial = ('```\n'
                     'filename = "Button_Press.py"\n'
                     '```')

        self.assertEqual(cleanup_codeblocks.fix_codeblocks(c_initial, None, self.logging), c_initial)


if __name__ == "__main__":
    unittest.main()
