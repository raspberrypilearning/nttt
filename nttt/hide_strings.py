"""
Generates the list of Crowdin string IDs that should be hidden from translators.

Reads the output of ``crowdin string list --verbose`` (on stdin) and prints, one
per line, the numeric ID of every string whose source text contains a marker
listed in the registry (see ``markers.py`` / ``markers.yml``). This replaces the
hand-written grep/awk/sed pipeline that used to live in ``hide-strings.yml`` and
covers both the legacy and RFM syntaxes.

Typical use in CI:

    crowdin string list --verbose | nttt --hide-strings > ids.txt
    while read -r id; do crowdin string edit "$id" --hidden; done < ids.txt
"""
import re
import sys
import html
from .markers import hideable_strings


# The verbose listing puts the string ID first, e.g. "#12345  source text ...".
_ID_RE = re.compile(r"^\s*#?(\d+)\b")
_LABELLED_ID_RE = re.compile(r"^\s*(?:string\s+)?id\s*:\s*#?(\d+)\b", re.IGNORECASE)
_ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[ -/]*[@-~]")
_ESCAPED_MARKDOWN_RE = re.compile(r"\\([\\`*_{}\[\]()#+\-.!<>/])")


def _normalise_for_marker_match(line):
    """Returns Crowdin CLI text with Markdown punctuation escapes removed."""
    line = _ANSI_RE.sub("", line)
    line = html.unescape(line)
    return _ESCAPED_MARKDOWN_RE.sub(r"\1", line)


def _string_id_from_line(line):
    """Returns a Crowdin string ID from a verbose/plain listing line, if present."""
    line = _ANSI_RE.sub("", line)
    id_match = _ID_RE.match(line) or _LABELLED_ID_RE.match(line)
    return id_match.group(1) if id_match else None


def find_hidden_strings(string_list_text, markers=None):
    """
    Returns a list of dicts ``{"id", "marker", "source"}`` for each line of the
    Crowdin listing whose source text contains a hideable marker.
    """
    markers = hideable_strings() if markers is None else markers
    results = []

    current_id = None

    for line in string_list_text.splitlines():
        string_id = _string_id_from_line(line)
        if string_id:
            current_id = string_id

        search_line = _normalise_for_marker_match(line)
        matched = next((marker for marker in markers if marker in search_line), None)
        if matched is None:
            continue

        if current_id:
            results.append({"id": current_id, "marker": matched, "source": line.strip()})

    return results


def unique_ids(results):
    """Returns the IDs from ``find_hidden_strings`` de-duplicated, order preserved."""
    seen = set()
    ids = []
    for result in results:
        if result["id"] not in seen:
            seen.add(result["id"])
            ids.append(result["id"])
    return ids


def format_report(results):
    """Human-readable 'id <- matched marker <- source' report, for inspection."""
    return "\n".join(
        "{id}\t{marker}\t{source}".format(**result) for result in results
    )


def run(input_stream=None, output_stream=None):
    """Reads a Crowdin listing from ``input_stream`` and prints IDs to hide."""
    input_stream = input_stream if input_stream is not None else sys.stdin
    output_stream = output_stream if output_stream is not None else sys.stdout

    results = find_hidden_strings(input_stream.read())
    for string_id in unique_ids(results):
        print(string_id, file=output_stream)
