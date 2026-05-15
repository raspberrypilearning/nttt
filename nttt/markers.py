import re


LINE_KIND_BARE_MARKER = "bare"
LINE_KIND_LABELLED_MARKER = "labelled"
LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE = "paired_empty_blockquote"
LINE_KIND_REGULAR = "regular"


RFM_BARE_MARKER_PATTERN = re.compile(
    r'^(?P<prefix>\s*(?:>\s*)+)\[!(?P<tag>[A-Z][A-Z0-9_-]*)\]\s*$'
)

RFM_LABELLED_MARKER_PATTERN = re.compile(
    r'^(?P<prefix>\s*(?:>\s*)+)\[!(?P<tag>[A-Z][A-Z0-9_-]*)\]\s+(?P<label>\S.*?)\s*$'
)

LEGACY_BARE_MARKER_PATTERN = re.compile(
    r'^\s*---\s+/?[\w-]+\s+---\s*$'
)

EMPTY_BLOCKQUOTE_PATTERN = re.compile(r'^\s*(?:>\s*)+$')
FENCE_LINE_PREFIX_PATTERN = re.compile(r'^\s*(?:>\s*)*')
SAME_LINE_FENCE_PATTERN = re.compile(r'^```[^`]*```$')


def remove_eol(line):
    return line.rstrip("\r\n")


def get_eol(line):
    if line.endswith("\r\n"):
        return "\r\n"
    if line.endswith("\n"):
        return "\n"
    if line.endswith("\r"):
        return "\r"
    return ""


def classify_line(line):
    line_without_eol = remove_eol(line)

    match = RFM_LABELLED_MARKER_PATTERN.match(line_without_eol)
    if match:
        return LINE_KIND_LABELLED_MARKER, match

    match = RFM_BARE_MARKER_PATTERN.match(line_without_eol)
    if match:
        return LINE_KIND_BARE_MARKER, match

    match = LEGACY_BARE_MARKER_PATTERN.match(line_without_eol)
    if match:
        return LINE_KIND_BARE_MARKER, match

    match = EMPTY_BLOCKQUOTE_PATTERN.match(line_without_eol)
    if match:
        return LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE, match

    return LINE_KIND_REGULAR, None


def is_marker_line(line):
    line_kind, _ = classify_line(line)
    return line_kind in (LINE_KIND_BARE_MARKER, LINE_KIND_LABELLED_MARKER)


def is_rfm_bare_marker_line(line):
    return RFM_BARE_MARKER_PATTERN.match(remove_eol(line)) is not None


def is_paired_empty_blockquote(line):
    line_kind, _ = classify_line(line)
    return line_kind == LINE_KIND_PAIRED_EMPTY_BLOCKQUOTE


def iter_lines_with_fence_state(content):
    inside_fenced_code = False

    for line in content.splitlines(keepends=True):
        yield line, inside_fenced_code
        if _count_fence_markers(line) % 2 == 1:
            inside_fenced_code = not inside_fenced_code


def _count_fence_markers(line):
    content = remove_eol(line)
    content_without_prefix = content[FENCE_LINE_PREFIX_PATTERN.match(content).end():]

    if not content_without_prefix.startswith("```"):
        return 0

    if SAME_LINE_FENCE_PATTERN.match(content_without_prefix):
        return 2

    return 1
