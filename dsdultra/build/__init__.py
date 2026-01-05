from dsdultra.util import is_windows


def build_executable():
    if is_windows():
        from dsdultra.build.win import build_executable
    else:
        from dsdultra.build.linux import build_executable
    build_executable()
