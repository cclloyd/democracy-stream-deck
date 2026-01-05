import sys


def is_frozen():
    """Check if running as a bundled executable (e.g., Nuitka, PyInstaller)."""
    return getattr(sys, 'frozen', False) or str(sys.argv[0]).lower().endswith('.exe')

def is_windows():
    return sys.platform == 'win32' or sys.platform == 'Windows'

def is_linux():
    return sys.platform == 'linux'
