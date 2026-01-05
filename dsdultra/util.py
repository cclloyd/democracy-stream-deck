import sys


def is_frozen():
    if getattr(sys, "frozen", False):
        return True
    # Nuitka sets at least one of these in compiled programs
    if getattr(sys, "nuitka_version", None) is not None:
        return True
    if globals().get("__compiled__", False):
        return True
    if str(sys.argv[0]).lower().endswith(".exe"):
        return True
    return False

def is_windows():
    return sys.platform == 'win32' or sys.platform == 'Windows'

def is_linux():
    return sys.platform == 'linux'
