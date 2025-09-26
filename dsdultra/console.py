import sys


def _is_frozen():
    # True when running from a bundled executable
    return bool(getattr(sys, 'frozen', False))


def show_console(icon=None, item=None):
    # Only show console if running from a bundled executable, otherwise it's already visible.
    if not _is_frozen():
        return

    pass