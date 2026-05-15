import os
import re
import sys
from .markers import (
    LEGACY_BARE_MARKER_PATTERN,
    LINE_KIND_BARE_MARKER,
    LINE_KIND_LABELLED_MARKER,
    LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE,
    LINE_KIND_REGULAR,
    classify_line,
    get_eol,
    iter_lines_with_fence_state,
    is_rfm_bare_marker_line,
    is_paired_empty_blockquote,
    remove_eol,
)
from .strip import strip_md
from .utilities import find_files, get_file, save_file


TRANSLATED_LABEL_PATTERN = re.compile(r'^(?P<prefix>\s*(?:>\s*)+)(?P<label>.*)$')

# Signals that the translated content is NOT in pure-stripped form and therefore
# does not need restoration. Pure-stripped output (from `nttt --mode strip`)
# cannot contain any of these:
#   - `\---` Crowdin escape sequence
#   - heading-jammed markers like `## --- collapse ---` or `## \--- collapse \---`
#   - canonical legacy bare markers (e.g. `--- collapse ---`)
_CROWDIN_ESCAPE_RE = re.compile(r'\\---')
_CROWDIN_HEADING_JAM_RE = re.compile(r'^\s*##\s+\\?---', re.MULTILINE)


def _looks_already_processed(translated_content):
    if _CROWDIN_ESCAPE_RE.search(translated_content):
        return True
    if _CROWDIN_HEADING_JAM_RE.search(translated_content):
        return True
    for line in translated_content.splitlines():
        if LEGACY_BARE_MARKER_PATTERN.match(line):
            return True
    return False


def restore_md(translated_content, english_content, file_label):
    if _looks_already_processed(translated_content):
        return translated_content

    translated_lines = translated_content.splitlines(keepends=True)
    expected_line_count = len(strip_md(english_content).splitlines(keepends=True))

    if len(translated_lines) != expected_line_count:
        print("Warning ({}): Different stripped structure in the original (en) and translated pages. "
              "Restoring stripped markers will not be performed. Expected {} translated lines, found {}.".format(
                  file_label,
                  expected_line_count,
                  len(translated_lines)),
              file=sys.stderr)
        return translated_content

    restored_lines = []
    translated_index = 0
    english_actions = _build_english_actions(english_content)

    for action_kind, english_line, match in english_actions:
        if action_kind in (LINE_KIND_BARE_MARKER, LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE):
            restored_lines.append(english_line)
            continue

        translated_line = translated_lines[translated_index]
        translated_index += 1

        if action_kind == LINE_KIND_LABELLED_MARKER:
            restored_lines.append(_restore_labelled_marker(english_line, match, translated_line))
        else:
            restored_lines.append(translated_line)

    return "".join(restored_lines)


def restore_tree(input_folder, english_folder, output_folder):
    files_to_restore = find_files(input_folder, extensions=[".md"])

    for source_file_path in files_to_restore:
        relative_file_name = os.path.relpath(source_file_path, input_folder)
        english_file_path = os.path.join(english_folder, relative_file_name)
        output_file_path = os.path.join(output_folder, relative_file_name)
        output_file_folder = os.path.dirname(output_file_path)

        if not os.path.exists(output_file_folder):
            os.makedirs(output_file_folder)

        content, suggested_eol = get_file(source_file_path)
        if os.path.isfile(english_file_path):
            english_content, _ = get_file(english_file_path)
            content = restore_md(content, english_content, relative_file_name)

        save_file(output_file_path, content, suggested_eol)


def _build_english_actions(english_content):
    lines_with_fence_state = list(iter_lines_with_fence_state(english_content))
    lines = [line for line, _ in lines_with_fence_state]
    outside_fence = [not inside for _, inside in lines_with_fence_state]
    actions = []
    index = 0

    while index < len(lines):
        line = lines[index]

        if not outside_fence[index]:
            actions.append((LINE_KIND_REGULAR, line, None))
            index += 1
            continue

        line_kind, match = classify_line(line)

        if line_kind == LINE_KIND_BARE_MARKER:
            actions.append((LINE_KIND_BARE_MARKER, line, match))
            if (
                is_rfm_bare_marker_line(line)
                and index + 1 < len(lines)
                and outside_fence[index + 1]
                and is_paired_empty_blockquote(lines[index + 1])
            ):
                actions.append((LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE, lines[index + 1], None))
                index += 2
            else:
                index += 1
            continue

        if line_kind == LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE:
            actions.append((LINE_KIND_REGULAR, line, None))
        else:
            actions.append((line_kind, line, match))
        index += 1

    return actions


def _restore_labelled_marker(english_line, english_match, translated_line):
    translated_label = _extract_translated_label(translated_line)
    return "{}[!{}] {}{}".format(
        english_match.group("prefix"),
        english_match.group("tag"),
        translated_label,
        get_eol(translated_line) or get_eol(english_line))


def _extract_translated_label(translated_line):
    line_without_eol = remove_eol(translated_line)
    match = TRANSLATED_LABEL_PATTERN.match(line_without_eol)
    if match:
        return match.group("label")
    return line_without_eol
