import re
from .constants import RegexConstants
from .nttt_logging import log_replacement


FENCE_PATTERN = re.compile(r'^(?P<indent>\s*)```(?P<info>.*)$')
ATTR_PATTERN = re.compile(
    rf'(?P<key>[\w-]+)[{RegexConstants.SPACES}]*=[{RegexConstants.SPACES}]*'
    rf'(?P<quote>[{RegexConstants.QUOTES}])(?P<value>.*?)(?P=quote)'
)

KNOWN_LANGUAGES = {
    "bash",
    "c",
    "cpp",
    "css",
    "html",
    "javascript",
    "js",
    "json",
    "markdown",
    "python",
    "scratch3",
    "shell",
    "text",
    "typescript",
    "yaml",
}


def fix_codeblocks(md_file_content, english_file_content, logging):
    english_infos = []
    if english_file_content is not None:
        english_infos = extract_opening_fence_infos(english_file_content)

    lines = md_file_content.split('\n')
    fixed_lines = []
    in_fence = False
    opening_fence_index = 0

    for line in lines:
        match = FENCE_PATTERN.match(line)
        if match:
            if not in_fence:
                english_info = None
                if opening_fence_index < len(english_infos):
                    english_info = english_infos[opening_fence_index]

                fixed_lines.append(fix_opening_fence(line, english_info, logging))
                opening_fence_index += 1
                in_fence = True
            else:
                fixed_lines.append(line)
                in_fence = False
        else:
            fixed_lines.append(line)

    return '\n'.join(fixed_lines)


def extract_opening_fence_infos(md_file_content):
    infos = []
    in_fence = False

    for line in md_file_content.split('\n'):
        match = FENCE_PATTERN.match(line)
        if match:
            if not in_fence:
                infos.append(match.group("info").strip())
                in_fence = True
            else:
                in_fence = False

    return infos


def fix_opening_fence(line, english_info, logging):
    match = FENCE_PATTERN.match(line)
    if match is None:
        return line

    info = normalise_quotes(match.group("info").strip())
    if info == "":
        return line

    fixed_info = normalise_info_string(info, english_info)
    replacement_text = "{}```{}".format(match.group("indent"), fixed_info)
    log_replacement(line, replacement_text, logging)
    return replacement_text


def normalise_info_string(info, english_info=None):
    attr_matches = list(ATTR_PATTERN.finditer(info))
    attr_start = attr_matches[0].start() if attr_matches else len(info)
    lang = info[:attr_start].strip().lower()

    if lang not in KNOWN_LANGUAGES and english_info:
        english_lang = extract_language(english_info)
        if english_lang:
            lang = english_lang

    attrs = []
    for match in attr_matches:
        key = match.group("key").lower()
        value = match.group("value").strip().lower()
        if key == "line_highlights":
            value = re.sub(r'\s+', '', value)
        attrs.append('{}="{}"'.format(key, value))

    if len(attrs) == 0:
        return lang

    if lang == "":
        return " ".join(attrs)

    return "{} {}".format(lang, " ".join(attrs))


def extract_language(info):
    info = normalise_quotes(info.strip())
    attr_match = ATTR_PATTERN.search(info)
    if attr_match:
        return info[:attr_match.start()].strip().lower()
    return info.strip().lower()


def normalise_quotes(text):
    for quote in RegexConstants.QUOTES:
        text = text.replace(quote, '"')
    return text
