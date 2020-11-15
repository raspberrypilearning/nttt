import re


def trim_formatting_tags(md_file_content, logging):
    return re.sub(r'(?P<last_word>\S+?)\s*{\s*:\s*(?P<tag>[\w]+?)\s*=\s*"(?P<value>.+?)"\s*}',
                  replacement_builder(logging),
                  md_file_content)


def replacement_builder(logging):
    def internal_replacement_builder(matchobj):
        original_text = matchobj.group()
        last_word = matchobj.group("last_word")
        tag_name = matchobj.group("tag")
        value = matchobj.group("value")

        replacement_text = '{}{{:{}="{}"}}'.format(last_word, tag_name, value)
        if logging == "on":
            display_replacement(original_text, replacement_text)

        return replacement_text

    return internal_replacement_builder


def display_replacement(text_before, text_after):
    # TODO think of using this approach in other cases as well
    if text_before != text_after:
        print("Replaced: {}".format(text_before))
        print("    with: {}".format(text_after))
