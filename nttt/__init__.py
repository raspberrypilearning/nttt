from .arguments import parse_command_line, resolve_arguments, check_arguments, show_arguments
from .constants import ArgumentKeyConstants, Modes
from .restore import restore_tree
from .strip import strip_tree
from .tidyup import tidyup_translations
from ._version import __version__

def main():
    command_line_args = parse_command_line(__version__)
    resolved_arguments = resolve_arguments(command_line_args)
    show_arguments(resolved_arguments)
    if (check_arguments(resolved_arguments)):
        mode = resolved_arguments[ArgumentKeyConstants.MODE]
        if mode == Modes.STRIP:
            strip_tree(
                resolved_arguments[ArgumentKeyConstants.INPUT],
                resolved_arguments[ArgumentKeyConstants.OUTPUT])
        elif mode == Modes.RESTORE:
            restore_tree(
                resolved_arguments[ArgumentKeyConstants.INPUT],
                resolved_arguments[ArgumentKeyConstants.ENGLISH],
                resolved_arguments[ArgumentKeyConstants.OUTPUT])
        else:
            tidyup_translations(resolved_arguments)
