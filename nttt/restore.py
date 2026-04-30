import io
import os
import shutil
import sys
from .constants import GeneralConstants
from .strip import PLACEHOLDER_PATTERN, TRANSLATABLE_META_KEYS, build_token_map, yaml_for_round_trip
from .utilities import get_file, save_file


def restore_tree(input_folder, english_folder, output_folder):
    for dname, _, files in os.walk(input_folder):
        for fname in files:
            if fname.endswith(".nttt.json"):
                continue

            source_file_path = os.path.join(dname, fname)
            relative_file_name = os.path.relpath(source_file_path, input_folder)
            english_file_path = os.path.join(english_folder, relative_file_name)
            output_file_path = os.path.join(output_folder, relative_file_name)
            output_file_folder = os.path.dirname(output_file_path)

            if not os.path.exists(output_file_folder):
                os.makedirs(output_file_folder)

            if fname == GeneralConstants.FILE_NAME_META_YML and os.path.isfile(english_file_path):
                restored_content, suggested_eol = restore_meta_file(source_file_path, english_file_path)
                save_file(output_file_path, restored_content, suggested_eol)
            elif os.path.splitext(fname)[1] == ".md" and os.path.isfile(english_file_path):
                restored_content, suggested_eol = restore_md_file(
                    source_file_path,
                    english_file_path,
                    relative_file_name)
                save_file(output_file_path, restored_content, suggested_eol)
            elif os.path.abspath(source_file_path) != os.path.abspath(output_file_path):
                shutil.copyfile(source_file_path, output_file_path)


def restore_md_file(source_file_path, english_file_path, relative_file_name):
    content, suggested_eol = get_file(source_file_path)
    english_content, _ = get_file(english_file_path)
    restored_content = restore_md(content, english_content, relative_file_name, source_file_path)
    return restored_content, suggested_eol


def restore_md(content, english_content, relative_file_name, md_file_name):
    token_map = build_token_map(relative_file_name, english_content)
    if "NTTT:" not in content:
        return content

    placeholders_in_content = set(match.group() for match in PLACEHOLDER_PATTERN.finditer(content))
    missing_placeholders = sorted(set(token_map) - placeholders_in_content)
    unknown_placeholders = sorted(placeholders_in_content - set(token_map))

    if missing_placeholders:
        print("Warning ({}): Missing NTTT placeholders: {}".format(
            md_file_name,
            ", ".join(missing_placeholders)), file=sys.stderr)

    if unknown_placeholders:
        print("Warning ({}): Unknown NTTT placeholders: {}".format(
            md_file_name,
            ", ".join(unknown_placeholders)), file=sys.stderr)

    restored_content = content
    for placeholder in token_map:
        restored_content = restored_content.replace(placeholder, token_map[placeholder]["value"])

    return restored_content


def restore_meta_file(source_file_path, english_file_path):
    content, suggested_eol = get_file(source_file_path)
    english_content, _ = get_file(english_file_path)
    return restore_meta_yaml(content, english_content), suggested_eol


def restore_meta_yaml(content, english_content):
    yaml_parser = yaml_for_round_trip()
    parsed_md = yaml_parser.load(content)
    english_parsed_md = yaml_parser.load(english_content)

    if parsed_md is None:
        return english_content

    if english_parsed_md is None:
        return content

    for key in TRANSLATABLE_META_KEYS:
        if key in parsed_md:
            english_parsed_md[key] = parsed_md[key]

    string_buffer = io.StringIO()
    yaml_parser.dump(english_parsed_md, string_buffer)
    return string_buffer.getvalue()
