import hashlib
import io
import json
import os
import re
import shutil
import ruamel.yaml
from .cleanup_alerts import ALERT_LINE_PATTERN, normalise_prefix
from .cleanup_codeblocks import FENCE_PATTERN
from .constants import GeneralConstants, RegexConstants
from .utilities import get_file, save_file


TRANSLATABLE_META_KEYS = ["title", "description", "steps", "meta_title", "meta_description"]
SECTION_PATTERN = re.compile(r'^(?P<indent>\s*)--- (?P<tag>.+?) ---(?P<trailing>\s*)$')
KRAMDOWN_CLASS_PATTERN = re.compile(rf'\{{:\s*class\s*=\s*[{RegexConstants.QUOTES}].+?[{RegexConstants.QUOTES}]\s*\}}')
HERO_IMAGE_PATTERN = re.compile(r'^(?P<indent>\s*)hero_image:\s+images/.+$')
PLACEHOLDER_PATTERN = re.compile(r'<!-- NTTT:(?P<token>[a-f0-9]{6}-\d{3}) -->')
YAML_PLACEHOLDER_PATTERN = re.compile(r'__NTTT_(?P<token>[a-f0-9]{6}_\d{3})__')


def strip_tree(input_folder, output_folder, debug_sidecars=False):
    for dname, _, files in os.walk(input_folder):
        for fname in files:
            source_file_path = os.path.join(dname, fname)
            relative_file_name = os.path.relpath(source_file_path, input_folder)
            output_file_path = os.path.join(output_folder, relative_file_name)
            output_file_folder = os.path.dirname(output_file_path)

            if not os.path.exists(output_file_folder):
                os.makedirs(output_file_folder)

            if fname == GeneralConstants.FILE_NAME_META_YML:
                stripped_content, token_map, suggested_eol = strip_meta_file(source_file_path, relative_file_name)
                save_file(output_file_path, stripped_content, suggested_eol)
            elif os.path.splitext(fname)[1] == ".md":
                stripped_content, token_map, suggested_eol = strip_md_file(source_file_path, relative_file_name)
                save_file(output_file_path, stripped_content, suggested_eol)
            else:
                shutil.copyfile(source_file_path, output_file_path)
                token_map = {}

            if debug_sidecars and token_map:
                write_debug_sidecar(output_file_path, source_file_path, token_map)


def strip_md_file(source_file_path, relative_file_name):
    content, suggested_eol = get_file(source_file_path)
    stripped_content, token_map = strip_md(content, relative_file_name)
    return stripped_content, token_map, suggested_eol


def strip_meta_file(source_file_path, relative_file_name):
    content, suggested_eol = get_file(source_file_path)
    stripped_content, token_map = strip_meta_yaml(content, relative_file_name)
    return stripped_content, token_map, suggested_eol


def strip_md(content, relative_file_name):
    generator = TokenGenerator(relative_file_name)
    token_map = {}
    stripped_lines = []
    in_fence = False

    for line in content.split('\n'):
        fence_match = FENCE_PATTERN.match(line)
        if fence_match:
            if not in_fence:
                info = fence_match.group("info").strip()
                if info:
                    placeholder = generator.next_markdown_placeholder()
                    token_map[placeholder] = {"kind": "code_fence_info", "value": info}
                    line = "{}```{}".format(fence_match.group("indent"), placeholder)
                in_fence = True
            else:
                in_fence = False

            stripped_lines.append(line)
            continue

        if in_fence:
            stripped_lines.append(line)
            continue

        section_match = SECTION_PATTERN.match(line)
        if section_match:
            placeholder = generator.next_markdown_placeholder()
            token_map[placeholder] = {"kind": "section", "value": line}
            stripped_lines.append("{}{}{}".format(
                section_match.group("indent"),
                placeholder,
                section_match.group("trailing")))
            continue

        hero_match = HERO_IMAGE_PATTERN.match(line)
        if hero_match:
            placeholder = generator.next_markdown_placeholder()
            token_map[placeholder] = {"kind": "hero_image", "value": line}
            stripped_lines.append("{}{}".format(hero_match.group("indent"), placeholder))
            continue

        line = strip_alert_line(line, generator, token_map)
        line = strip_kramdown_classes(line, generator, token_map)
        stripped_lines.append(line)

    return '\n'.join(stripped_lines), token_map


def strip_alert_line(line, generator, token_map):
    match = ALERT_LINE_PATTERN.match(line)
    if match is None:
        return line

    placeholder = generator.next_markdown_placeholder()
    token_map[placeholder] = {
        "kind": "alert_type",
        "value": "[!{}]".format(match.group("alert_type").strip().upper()),
    }
    prefix = normalise_prefix(match.group("prefix"))
    return "{}{}{}{}".format(match.group("indent"), prefix, placeholder, match.group("rest"))


def strip_kramdown_classes(line, generator, token_map):
    def replace(match):
        placeholder = generator.next_markdown_placeholder()
        token_map[placeholder] = {"kind": "kramdown_class", "value": match.group()}
        return placeholder

    return KRAMDOWN_CLASS_PATTERN.sub(replace, line)


def strip_meta_yaml(content, relative_file_name):
    yaml_parser = yaml_for_round_trip()
    parsed_md = yaml_parser.load(content)
    if parsed_md is None:
        return content, {}

    stripped_md = type(parsed_md)()
    for key in parsed_md:
        if key in TRANSLATABLE_META_KEYS:
            stripped_md[key] = parsed_md[key]

    string_buffer = io.StringIO()
    yaml_parser.dump(stripped_md, string_buffer)
    return string_buffer.getvalue(), {}


def build_token_map(relative_file_name, content):
    _, token_map = strip_md(content, relative_file_name)
    return token_map


def write_debug_sidecar(output_file_path, source_file_path, token_map):
    source_content, _ = get_file(source_file_path)
    sidecar = {
        "version": 1,
        "source_sha256": hashlib.sha256(source_content.encode("utf-8")).hexdigest(),
        "tokens": normalise_token_map_for_json(token_map),
    }
    with open(output_file_path + ".nttt.json", encoding="utf-8", mode="w") as f:
        json.dump(sidecar, f, indent=2, ensure_ascii=False)


def normalise_token_map_for_json(token_map):
    tokens = {}
    for placeholder in token_map:
        token = placeholder_to_token(placeholder)
        tokens[token[-3:]] = token_map[placeholder]
    return tokens


def placeholder_to_token(placeholder):
    match = PLACEHOLDER_PATTERN.search(placeholder)
    if match:
        return match.group("token")
    match = YAML_PLACEHOLDER_PATTERN.search(placeholder)
    if match:
        return match.group("token").replace("_", "-")
    return placeholder


def yaml_for_round_trip():
    yaml_parser = ruamel.yaml.YAML(typ='rt')
    yaml_parser.preserve_quotes = True
    yaml_parser.constructor.yaml_constructors.pop(u'tag:yaml.org,2002:timestamp', None)
    yaml_parser.indent(sequence=4, offset=2)
    yaml_parser.explicit_start = True
    yaml_parser.width = 1000000
    return yaml_parser


class TokenGenerator:
    def __init__(self, relative_file_name):
        self.salt = hashlib.sha256(relative_file_name.encode("utf-8")).hexdigest()[:6]
        self.index = 0

    def next_markdown_placeholder(self):
        self.index += 1
        return "<!-- NTTT:{}-{:03d} -->".format(self.salt, self.index)

    def next_yaml_placeholder(self):
        self.index += 1
        return "__NTTT_{}_{:03d}__".format(self.salt, self.index)
