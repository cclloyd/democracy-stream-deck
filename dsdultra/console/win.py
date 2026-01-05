import sys
import ctypes
from ctypes import wintypes

from dsdultra.util import is_frozen


def _has_console():
    GetConsoleWindow = ctypes.windll.kernel32.GetConsoleWindow
    GetConsoleWindow.restype = wintypes.HWND
    return bool(GetConsoleWindow())


# Buffered stream that captures writes until the real console is shown.
class _BufferedStream:
    def __init__(self, name=''):
        self._chunks = []
        self.name = name
        self.encoding = 'utf-8'

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)
        self._chunks.append(s)

    def flush(self):
        pass

    def isatty(self):
        return False

    def dump_to(self, fp):
        if not self._chunks:
            return
        fp.write(''.join(self._chunks))
        fp.flush()
        self._chunks.clear()

# Install buffering for stdout/stderr only when running from the exe and there is no console
_console_shown = False
if is_frozen() and not _has_console():
    _buffer_out = _BufferedStream('stdout')
    _buffer_err = _BufferedStream('stderr')
    sys.stdout = _buffer_out
    sys.stderr = _buffer_err
else:
    _buffer_out = None
    _buffer_err = None

# This is the function that is bound to the console menu item.
def show_console(icon=None, item=None):
    # Only relevant for the bundled exe; when running via python, assume console exists.
    if not is_frozen():
        return
    # If a console is already present, nothing to do.
    if _has_console():
        return

    global _console_shown
    if _console_shown:
        return

    kernel32 = ctypes.windll.kernel32
    user32 = ctypes.windll.user32

    ATTACH_PARENT_PROCESS = 0xFFFFFFFF
    SW_SHOW = 5
    SW_SHOWNORMAL = 1

    # Detach any stale console association then try to attach; if that fails, allocate.
    kernel32.FreeConsole()
    attached = bool(kernel32.AttachConsole(ATTACH_PARENT_PROCESS))
    if not attached:
        if not kernel32.AllocConsole():
            return  # Failed to create a console

    # UTF-8 I/O
    kernel32.SetConsoleOutputCP(65001)
    kernel32.SetConsoleCP(65001)

    # Bind stdio to the console
    con_out = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
    con_err = open('CONOUT$', 'w', encoding='utf-8', buffering=1)
    con_in = open('CONIN$', 'r', encoding='utf-8', buffering=1)

    # Flush buffered logs captured since launch
    if isinstance(sys.stdout, _BufferedStream):
        sys.stdout.dump_to(con_out)
    if isinstance(sys.stderr, _BufferedStream):
        sys.stderr.dump_to(con_err)

    sys.stdout = con_out
    sys.stderr = con_err
    sys.stdin = con_in

    # Show and focus the console window
    kernel32.SetConsoleTitleW("Democracy StreamDeck Console")
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        user32.ShowWindow(wintypes.HWND(hwnd), SW_SHOW)
        user32.ShowWindow(wintypes.HWND(hwnd), SW_SHOWNORMAL)
        user32.SetForegroundWindow(wintypes.HWND(hwnd))

    _console_shown = True