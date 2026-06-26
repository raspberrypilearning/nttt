from .arguments import parse_command_line, resolve_arguments, check_arguments, show_arguments
from .tidyup import tidyup_translations
from .hide_strings import run as run_hide_strings
from ._version import __version__

def main():
    command_line_args = parse_command_line(__version__)

    # Hide-strings mode: generate the Crowdin hide-list from stdin and exit.
    if getattr(command_line_args, "hide_strings", False):
        run_hide_strings()
        return

    # Unhide-strings mode: generate the Crowdin unhide-list from stdin and exit.
    if getattr(command_line_args, "unhide_strings", False):
        run_hide_strings(unhide=True)
        return

    resolved_arguments = resolve_arguments(command_line_args)
    show_arguments(resolved_arguments)
    if (check_arguments(resolved_arguments)):
        tidyup_translations(resolved_arguments)
