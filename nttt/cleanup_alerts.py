import re
import sys
from .constants import RegexConstants
from .nttt_logging import log_replacement


ALERT_LINE_PATTERN = re.compile(
    rf'^(?P<indent>[{RegexConstants.SPACES}]*)'
    rf'(?P<prefix>(?:>[{RegexConstants.SPACES}]*)+)'
    rf'[\[［][{RegexConstants.SPACES}]*![{RegexConstants.SPACES}]*'
    rf'(?P<alert_type>[^\]］]+?)'
    rf'[{RegexConstants.SPACES}]*[\]］]'
    rf'(?P<rest>.*)$'
)


def fix_alerts(md_file_content, logging):
    lines = md_file_content.split('\n')
    fixed_lines = []

    for line in lines:
        fixed_lines.append(fix_alert_line(line, logging))

    return '\n'.join(fixed_lines)


def fix_alert_line(line, logging):
    match = ALERT_LINE_PATTERN.match(line)
    if match is None:
        return line

    alert_type = match.group("alert_type").strip().upper()
    prefix = normalise_prefix(match.group("prefix"))
    replacement_text = "{}{}[!{}]{}".format(
        match.group("indent"),
        prefix,
        alert_type,
        match.group("rest"))

    log_replacement(line, replacement_text, logging)
    return replacement_text


def normalise_prefix(prefix):
    depth = prefix.count(">")
    return "> " * depth


def revert_alert_translation(md_file_name, md_file_content, en_file_content, logging):
    md_file_lines = md_file_content.split('\n')
    md_alerts = extract_alerts(md_file_lines)

    en_file_lines = en_file_content.split('\n')
    en_alerts = extract_alerts(en_file_lines)

    if len(md_alerts) == len(en_alerts):
        for i in range(len(md_alerts)):
            md_alert = md_alerts[i]
            en_alert = en_alerts[i]

            if md_alert["depth"] != en_alert["depth"]:
                return warn_and_skip(md_file_name, md_file_content)

            replacement_text = "{}{}[!{}]{}".format(
                md_alert["indent"],
                md_alert["prefix"],
                en_alert["alert_type"],
                md_alert["rest"])
            log_replacement(md_file_lines[md_alert["line_num"]], replacement_text, logging)
            md_file_lines[md_alert["line_num"]] = replacement_text

        return '\n'.join(md_file_lines)
    else:
        return warn_and_skip(md_file_name, md_file_content)


def warn_and_skip(md_file_name, md_file_content):
    print("Warning ({}): Different alert structure in the original (en) and the translated pages. "
          "Reverting of translated alert types will not be performed".format(md_file_name), file=sys.stderr)
    return md_file_content


def extract_alerts(md_file_lines):
    alerts = []

    for i in range(len(md_file_lines)):
        line = fix_alert_line(md_file_lines[i], "off")
        match = ALERT_LINE_PATTERN.match(line)
        if match:
            prefix = normalise_prefix(match.group("prefix"))
            alerts.append({
                "line_num": i,
                "indent": match.group("indent"),
                "prefix": prefix,
                "depth": prefix.count(">"),
                "alert_type": match.group("alert_type").strip().upper(),
                "rest": match.group("rest"),
            })

    return alerts
