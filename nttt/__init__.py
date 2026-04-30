import os
from .arguments import parse_command_line, resolve_arguments, check_arguments, show_arguments
from .arguments import get_absolute_path, get_final_step
from .constants import ArgumentKeyConstants
from .restore import restore_tree
from .strip import strip_tree
from .tidyup import tidyup_translations
from ._version import __version__


def main():
    command_line_args = parse_command_line(__version__)
    command = getattr(command_line_args, "command", None)

    if command == "strip":
        strip_tree(
            get_absolute_path(command_line_args.input),
            get_absolute_path(command_line_args.output),
            command_line_args.debug_sidecars)
        return

    if command == "restore":
        restore_tree(
            get_absolute_path(command_line_args.input),
            get_absolute_path(command_line_args.english),
            get_absolute_path(command_line_args.output))

        if command_line_args.then_tidyup:
            restored_arguments = build_restore_tidyup_arguments(command_line_args)
            show_arguments(restored_arguments)
            if check_arguments(restored_arguments):
                tidyup_translations(restored_arguments)
        return

    resolved_arguments = resolve_arguments(command_line_args)
    show_arguments(resolved_arguments)
    if (check_arguments(resolved_arguments)):
        tidyup_translations(resolved_arguments)


def build_restore_tidyup_arguments(command_line_args):
    input_folder = get_absolute_path(command_line_args.input)
    output_folder = get_absolute_path(command_line_args.output)
    english_folder = get_absolute_path(command_line_args.english)

    arguments = {}
    arguments[ArgumentKeyConstants.INPUT] = output_folder
    arguments[ArgumentKeyConstants.OUTPUT] = output_folder
    arguments[ArgumentKeyConstants.ENGLISH] = english_folder
    arguments[ArgumentKeyConstants.LANGUAGE] = os.path.basename(input_folder)
    arguments[ArgumentKeyConstants.VOLUNTEERS] = []
    arguments[ArgumentKeyConstants.FINAL] = get_final_step(output_folder)

    if getattr(command_line_args, "Disable", False):
        arguments[ArgumentKeyConstants.DISABLE] = command_line_args.Disable.split(",")
    else:
        arguments[ArgumentKeyConstants.DISABLE] = []

    if getattr(command_line_args, "Logging", False):
        arguments[ArgumentKeyConstants.LOGGING] = command_line_args.Logging
    else:
        arguments[ArgumentKeyConstants.LOGGING] = "off"

    if getattr(command_line_args, "Yes", False):
        arguments[ArgumentKeyConstants.YES] = command_line_args.Yes
    else:
        arguments[ArgumentKeyConstants.YES] = "off"

    return arguments
