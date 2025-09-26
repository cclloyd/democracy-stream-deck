import ctypes
import os
import sys
import time
from ctypes import wintypes

from nuitka.__main__ import main as nuitka_main


def is_process_running_by_path(target_path: str) -> bool:
    target_path = os.path.abspath(target_path)
    target_norm = os.path.normcase(target_path)

    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    # DWORD array for PIDs
    arr_size = 4096
    pid_array = (wintypes.DWORD * arr_size)()
    bytes_returned = wintypes.DWORD(0)

    if not psapi.EnumProcesses(pid_array, ctypes.sizeof(pid_array), ctypes.byref(bytes_returned)):
        return False

    count = bytes_returned.value // ctypes.sizeof(wintypes.DWORD)

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    OpenProcess = kernel32.OpenProcess
    CloseHandle = kernel32.CloseHandle

    # BOOL QueryFullProcessImageNameW(HANDLE, DWORD, LPWSTR, PDWORD)
    QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
    QueryFullProcessImageNameW.restype = wintypes.BOOL
    QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]

    for i in range(count):
        pid = pid_array[i]
        if pid == 0:
            continue
        hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not hProc:
            continue
        try:
            buf_len = wintypes.DWORD(32768)  # large enough for long paths
            buf = ctypes.create_unicode_buffer(buf_len.value)
            if QueryFullProcessImageNameW(hProc, 0, buf, ctypes.byref(buf_len)):
                exe_path = os.path.normcase(buf.value)
                if exe_path == target_norm:
                    return True
        finally:
            CloseHandle(hProc)
    return False

def _get_pids_by_path(target_path: str) -> list[int]:
    target_path = os.path.abspath(target_path)
    target_norm = os.path.normcase(target_path)

    psapi = ctypes.WinDLL('psapi', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    arr_size = 4096
    pid_array = (wintypes.DWORD * arr_size)()
    bytes_returned = wintypes.DWORD(0)

    if not psapi.EnumProcesses(pid_array, ctypes.sizeof(pid_array), ctypes.byref(bytes_returned)):
        return []

    count = bytes_returned.value // ctypes.sizeof(wintypes.DWORD)

    PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
    OpenProcess = kernel32.OpenProcess
    CloseHandle = kernel32.CloseHandle

    QueryFullProcessImageNameW = kernel32.QueryFullProcessImageNameW
    QueryFullProcessImageNameW.restype = wintypes.BOOL
    QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR, ctypes.POINTER(wintypes.DWORD)]

    pids = []
    for i in range(count):
        pid = pid_array[i]
        if pid == 0:
            continue
        hProc = OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
        if not hProc:
            continue
        try:
            buf_len = wintypes.DWORD(32768)
            buf = ctypes.create_unicode_buffer(buf_len.value)
            if QueryFullProcessImageNameW(hProc, 0, buf, ctypes.byref(buf_len)):
                exe_path = os.path.normcase(buf.value)
                if exe_path == target_norm:
                    pids.append(int(pid))
        finally:
            CloseHandle(hProc)
    return pids

def _post_wm_close_to_pid(pid: int) -> None:
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)

    EnumWindows = user32.EnumWindows
    EnumWindowsProc = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    GetWindowThreadProcessId = user32.GetWindowThreadProcessId
    IsWindowVisible = user32.IsWindowVisible
    PostMessageW = user32.PostMessageW

    WM_CLOSE = 0x0010

    target_pid = wintypes.DWORD(pid)

    def callback(hwnd, lParam):
        _pid = wintypes.DWORD()
        GetWindowThreadProcessId(hwnd, ctypes.byref(_pid))
        if _pid.value == target_pid.value and IsWindowVisible(hwnd):
            # Post WM_CLOSE to visible top-level windows of the process
            PostMessageW(hwnd, WM_CLOSE, 0, 0)
        return True

    EnumWindows(EnumWindowsProc(callback), 0)

def _terminate_pid(pid: int) -> bool:
    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
    PROCESS_TERMINATE = 0x0001
    OpenProcess = kernel32.OpenProcess
    TerminateProcess = kernel32.TerminateProcess
    CloseHandle = kernel32.CloseHandle

    hProc = OpenProcess(PROCESS_TERMINATE, False, pid)
    if not hProc:
        return False
    try:
        ok = TerminateProcess(hProc, 1)  # exit code 1
        return bool(ok)
    finally:
        CloseHandle(hProc)

def _wait_until_pids_exit(pids: list[int], timeout: float) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        alive = []
        for pid in pids:
            try:
                # Check if process handle can be opened with minimal rights
                kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
                h = kernel32.OpenProcess(PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                if h:
                    kernel32.CloseHandle(h)
                    alive.append(pid)
            except Exception:
                # If OpenProcess fails, assume it might be gone
                pass
        if not alive:
            return True
        time.sleep(0.2)
    return False

def try_close_by_path(target_path: str, gentle_timeout: float = 3.0, force_timeout: float = 3.0) -> bool:
    '''
    Attempts to close processes running from target_path.
    1) Post WM_CLOSE to their top-level windows (gentle).
    2) Wait up to gentle_timeout.
    3) If still alive, call TerminateProcess (force).
    4) Wait up to force_timeout.

    Returns True if all target processes exited; False otherwise.
    '''
    pids = _get_pids_by_path(target_path)
    if not pids:
        return True

    # Gentle close
    for pid in pids:
        _post_wm_close_to_pid(pid)
    if _wait_until_pids_exit(pids, gentle_timeout):
        return True

    # Force terminate remaining
    remaining = _get_pids_by_path(target_path)
    for pid in remaining:
        _terminate_pid(pid)

    return _wait_until_pids_exit(remaining, force_timeout)

def build_executable():
    target = 'build/dsd.exe'

    # Check if output file is running, and attempt to close
    if not try_close_by_path(target):
        input(f'{target} is running and could not be closed automatically. Close it, then press Enter to continue...')

    sys.argv = [
        'nuitka',  # dummy program name
        '--onefile',
        '--include-data-dir=dsdultra/assets=dsdultra/assets',
        '--standalone',
        '--assume-yes-for-downloads',
        f'--output-filename=dsd.exe',
        '--enable-plugin=tk-inter',
        '--no-deployment-flag=self-execution',
        '--windows-console-mode=force',  # force/hide/disable/attach
        '--windows-icon-from-ico=dsdultra/assets/icons/DSDIcon.ico',
        '--nofollow-import-to=dsdultra.build',
        '--output-dir=build',
        'dsdultra/__main__.py',
    ]
    nuitka_main()
