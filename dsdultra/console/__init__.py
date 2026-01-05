from dsdultra.util import is_windows


def show_console():
    if is_windows():
       from .win import show_console as con
    else:
        from .linux import show_console as con
    con()