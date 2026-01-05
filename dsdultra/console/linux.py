import os
import sys
import shlex
import shutil
import tempfile
import subprocess
from pathlib import Path

from dsdultra.util import is_frozen


# Buffered/tee stream that writes to a logfile (and optionally to an original stream).
class _TeeLogStream:
    def __init__(self, log_fp, orig=None, name=''):
        self._log_fp = log_fp
        self._orig = orig
        self.name = name
        self.encoding = 'utf-8'

    def write(self, s):
        if not isinstance(s, str):
            s = str(s)

        try:
            self._log_fp.write(s)
            self._log_fp.flush()
        except Exception:
            pass

        if self._orig is not None:
            try:
                self._orig.write(s)
                self._orig.flush()
            except Exception:
                pass

    def flush(self):
        try:
            self._log_fp.flush()
        except Exception:
            pass
        if self._orig is not None:
            try:
                self._orig.flush()
            except Exception:
                pass

    def isatty(self):
        return False


_console_proc: subprocess.Popen | None = None
_log_path: Path | None = None

# When running from the bundled binary, capture stdout/stderr into a temp logfile
# so we can show it in a terminal later.
if is_frozen():
    try:
        log_dir = Path(tempfile.gettempdir()) / 'dsdultra'
        log_dir.mkdir(parents=True, exist_ok=True)

        pid = os.getpid()
        _log_path = log_dir / f'dsdultra-{pid}.log'

        # line-buffered text writes
        _log_fp = open(_log_path, 'a', encoding='utf-8', buffering=1)

        _orig_out = sys.stdout
        _orig_err = sys.stderr

        sys.stdout = _TeeLogStream(_log_fp, orig=_orig_out, name='stdout')
        sys.stderr = _TeeLogStream(_log_fp, orig=_orig_err, name='stderr')
    except Exception:
        # If anything about logging setup fails, don't break the app.
        _log_path = None


def _pick_terminal_command() -> list[str] | None:
    '''
    Best-effort choice of a terminal emulator command.
    Returns argv (without the command to run inside), or None if unavailable.
    '''
    # Prefer system default where available.
    candidates = [
        ['x-terminal-emulator', '-e'],  # Debian/Ubuntu alternatives system
        ['konsole', '-e'],              # KDE
        ['gnome-terminal', '--'],
        ['xfce4-terminal', '-e'],
        ['mate-terminal', '-e'],
        ['lxterminal', '-e'],
        ['kitty', '-e'],
        ['alacritty', '-e'],
        ['xterm', '-e'],
    ]
    for cmd in candidates:
        if shutil.which(cmd[0]):
            return cmd
    return None


def show_console(*args, **kwargs):
    """
    Linux implementation: open a terminal window showing a live view of the app log.

    Notes:
    - Only enabled for the final bundled binary (frozen build).
    - Uses a temp logfile and tails it in a terminal emulator.
    """
    if not is_frozen():
        return

    # If we have no GUI session, spawning a terminal won't work.
    if not (os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY')):
        return

    if _log_path is None:
        return

    term = _pick_terminal_command()
    if term is None:
        return

    global _console_proc
    if _console_proc is not None and _console_proc.poll() is None:
        # Terminal is still open; don't spawn duplicates.
        return

    term = _pick_terminal_command()
    if term is None:
        return

    # Use a shell wrapper so we can set a title and run tail reliably.
    # tail -n +1: show the whole file; -F: follow by name (handles truncation/rotation)
    log_file = str(_log_path)
    shell_cmd = (
        f'printf "\\033]0;%s\\007" "Democracy StreamDeck Console"; '
        f'echo "Logging to: {shlex.quote(log_file)}"; '
        f'echo; '
        f'exec tail -n +1 -F {shlex.quote(log_file)}'
    )

    try:
        _console_proc = subprocess.Popen(
            [*term, 'sh', '-lc', shell_cmd],
            close_fds=True,
            env=os.environ.copy(),
        )
    except Exception:
        # Don't crash the app if the terminal launch fails.
        _console_proc = None
        return

