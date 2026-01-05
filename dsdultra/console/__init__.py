import sys


def show_console():
    if sys.platform == 'win32' or sys.platform == 'Windows':
       from .win import show_console as con
    else:
        from .linux import show_console as con
    con()