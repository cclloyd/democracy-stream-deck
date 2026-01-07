import tempfile
import traceback
from datetime import datetime
from pathlib import Path
import subprocess

from dsdultra.util import is_frozen, is_windows


_console_proc: subprocess.Popen | None = None


def _ps_single_quote(s: str) -> str:
    return s.replace("'", "''")


def show_console(log_path: Path, **kwargs):
    global _console_proc
    print(f'Showing console for {log_path}')

    if not is_frozen():
        return
    if not is_windows():
        return
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        log_path.touch(exist_ok=True)

        # If a terminal window is already open, don't open a second one.
        if _console_proc is not None and _console_proc.poll() is None:
            return

        ps_path = _ps_single_quote(str(log_path))
        ps_cmd = (
            f"$host.ui.RawUI.WindowTitle = 'dsdultra logs'; "
            f"Write-Host 'Tailing: {ps_path}'; "
            f"Get-Content -LiteralPath '{ps_path}' -Wait -Tail 200"
        )

        creationflags = subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP

        _console_proc = subprocess.Popen(
            ['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', ps_cmd],
            creationflags=creationflags,
            close_fds=False,
        )
    except Exception:
        traceback.print_exc()

