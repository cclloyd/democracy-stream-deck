from dsdultra.util import is_frozen


def show_console(*args, **kwargs):
    if not is_frozen():
        return

