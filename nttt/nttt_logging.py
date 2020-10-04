def display_md(tag_name, text_before, text_after):
    if text_before != text_after:
        print("Replaced: {}{}{}".format(tag_name, text_before, tag_name))
        print("    with: {}{}{}".format(tag_name, text_after, tag_name))


def display_tags(tag_name, text_before, text_after):
    if text_before != text_after:
        print("Replaced: <{}>{}</{}>".format(tag_name, text_before, tag_name))
        print("    with: <{}>{}</{}>".format(tag_name, text_after, tag_name))