import os
from .markers import (
    LINE_KIND_BARE_MARKER,
    LINE_KIND_LABELLED_MARKER,
    classify_line,
    get_eol,
    is_rfm_bare_marker_line,
    is_paired_empty_blockquote,
)
from .utilities import find_files, get_file, save_file


def strip_md(content):
    parts = content.split("```")
    processed_parts = []

    for index in range(len(parts)):
        if (index % 2) == 0:
            processed_parts.append(_strip_md_outside_fences(parts[index]))
        else:
            processed_parts.append(parts[index])

    return "```".join(processed_parts)


def _strip_md_outside_fences(content):
    lines = content.splitlines(keepends=True)
    stripped_lines = []
    index = 0

    while index < len(lines):
        line = lines[index]
        line_kind, match = classify_line(line)

        if line_kind == LINE_KIND_BARE_MARKER:
            if (
                is_rfm_bare_marker_line(line)
                and index + 1 < len(lines)
                and is_paired_empty_blockquote(lines[index + 1])
            ):
                index += 2
            else:
                index += 1
            continue

        if line_kind == LINE_KIND_LABELLED_MARKER:
            stripped_lines.append("{}{}{}".format(
                match.group("prefix"),
                match.group("label"),
                get_eol(line)))
            index += 1
            continue

        stripped_lines.append(line)
        index += 1

    return "".join(stripped_lines)


def strip_tree(input_folder, output_folder):
    files_to_strip = find_files(input_folder, extensions=[".md"])

    for source_file_path in files_to_strip:
        relative_file_name = os.path.relpath(source_file_path, input_folder)
        output_file_path = os.path.join(output_folder, relative_file_name)
        output_file_folder = os.path.dirname(output_file_path)

        if not os.path.exists(output_file_folder):
            os.makedirs(output_file_folder)

        content, suggested_eol = get_file(source_file_path)
        save_file(output_file_path, strip_md(content), suggested_eol)
