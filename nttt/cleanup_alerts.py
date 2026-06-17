"""
Clean-up for Raspberry Flavoured Markdown (RFM) blockquote alerts, e.g.

    > [!TASK]
    > [!HINT]
    > [!ACCORDION] Downloading the software

This mirrors ``cleanup_sections.py`` (which handles the legacy ``--- task ---``
syntax). Both run on every file, so a file may freely mix the two syntaxes.
"""
import re
import sys
from .nttt_logging import log_replacement


# Matches a blockquote alert header line. Tolerates:
#   * a missing/extra space after '>'      ( ">[!TASK]" )
#   * spaces inside the brackets           ( "> [! TASK ]" )
#   * a Crowdin backslash escape           ( "> \[!TASK]" )
#   * nested blockquote levels             ( "> > [!HINT]" )
# Captures the blockquote prefix, the keyword, and any trailing title text
# (the title is translatable, e.g. for ACCORDION, so it is preserved).
_ALERT_HEADER_RE = re.compile(
    r"^(?P<prefix>[ \t]*(?:>[ \t]*)+)\\?\[!\s*(?P<kw>[^\]\r\n]+?)\s*\](?P<title>[ \t]*[^\r\n]*)$",
    re.MULTILINE,
)


def _normalise_prefix(prefix):
    """Collapse a blockquote prefix to one space after each '>' ("> > ")."""
    levels = prefix.count(">")
    return "> " * levels


def _format_alert(prefix, keyword, title):
    new_prefix = _normalise_prefix(prefix)
    title = title.strip()
    new_title = (" " + title) if title else ""
    return f"{new_prefix}[!{keyword}]{new_title}"


def fix_alerts(md_file_content, logging):
    """Normalise RFM alert header spacing/case (e.g. ">[! task ]" -> "> [!TASK]")."""

    def replacement(matchobj):
        keyword = matchobj.group("kw").strip().upper()
        new_line = _format_alert(matchobj.group("prefix"), keyword, matchobj.group("title"))
        log_replacement(matchobj.group(0), new_line, logging)
        return new_line

    return _ALERT_HEADER_RE.sub(replacement, md_file_content)


def revert_alert_translation(md_file_name, md_file_content, en_file_content, logging):
    """
    Reverts translated alert keywords back to English (e.g. "> [!TAREA]" ->
    "> [!TASK]") by position against the English file, keeping any translated
    title text. Only runs when the alert counts match, mirroring
    ``revert_section_translation``.
    """
    md_lines = md_file_content.split("\n")
    en_lines = en_file_content.split("\n")

    md_indices = [i for i, line in enumerate(md_lines) if _ALERT_HEADER_RE.match(line)]
    en_keywords = [
        _ALERT_HEADER_RE.match(line).group("kw").strip().upper()
        for line in en_lines
        if _ALERT_HEADER_RE.match(line)
    ]

    if len(md_indices) != len(en_keywords):
        print(
            "Warning ({}): Different alert structure in the original (en) and the "
            "translated pages. Reverting of translated alert keywords will not be "
            "performed".format(md_file_name),
            file=sys.stderr,
        )
        return md_file_content

    for position, line_index in enumerate(md_indices):
        match = _ALERT_HEADER_RE.match(md_lines[line_index])
        new_line = _format_alert(match.group("prefix"), en_keywords[position], match.group("title"))
        log_replacement(md_lines[line_index], new_line, logging)
        md_lines[line_index] = new_line

    return "\n".join(md_lines)
