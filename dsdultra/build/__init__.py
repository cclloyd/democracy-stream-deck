import sys


def build_executable():
    if sys.platform == 'win32':
        from dsdultra.build.win import build_executable
    else:
        from dsdultra.build.linux import build_executable
    build_executable()
