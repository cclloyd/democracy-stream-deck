import ctypes
import os
import shutil
import sys
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox

from dsdultra import ASSETS_DIR


def is_user_admin():
    """Check if the user has admin privileges on Windows."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def elevate_self_for_install():
    """
    Relaunches this script with admin rights to perform installation.
    """
    print(sys.executable, sys.argv)
    if getattr(sys, 'frozen', False):  # If running as an .exe (PyInstaller, etc)
        exe = sys.executable
        params = ' '.join([f'"{arg}"' for arg in sys.argv])
    else:
        exe = sys.executable
        params = '-m dsdultra install' if 'python' in exe.lower() else 'install'

    try:
        ret = ctypes.windll.shell32.ShellExecuteW(
            None,
            "runas",
            exe,
            params,
            None,
            1
        )
        return ret > 32
    except Exception as e:
        print(f"Failed to elevate: {e}")
        return False

def prompt_library_install():
    def open_link(event=None):
        webbrowser.open('https://github.com/libusb/hidapi/releases')

    # Custom dialog using tkinter
    root = tk.Tk()
    root.withdraw()  # Hide the main window

    dialog = tk.Toplevel(root)
    dialog.title('Missing hidapi.dll')
    dialog.resizable(False, False)
    dialog.grab_set()  # Make modal
    dialog.geometry('+{}+{}'.format(root.winfo_screenwidth() // 2 - 240, root.winfo_screenheight() // 2 - 120))

    msg = (
        'hidapi.dll is missing (No suitable LibUSB driver in any PATH directory).\n\n'
        'Would you like to install \'hidapi.dll\' to your System32 folder?\n'
    )

    tk.Label(dialog, text=msg, justify='left', wraplength=400).pack(padx=20, pady=(15, 3))

    # Add clickable link
    link = tk.Label(
        dialog,
        text='View/download hidapi releases',
        fg='blue',
        cursor='hand2',
        font=('Arial', 10, 'underline')
    )
    link.pack()
    link.bind('<Button-1>', open_link)

    # Variable for dialog response
    response = {'ans': None}

    def on_yes():
        response['ans'] = True
        dialog.destroy()
        root.destroy()

    def on_no():
        response['ans'] = False
        dialog.destroy()
        root.destroy()

    # Yes/No buttons
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text='Yes', width=10, command=on_yes).pack(side='left', padx=10)
    tk.Button(button_frame, text='No', width=10, command=on_no).pack(side='right', padx=10)

    # Center window
    dialog.update_idletasks()
    dialog.lift()
    dialog.attributes('-topmost', True)
    dialog.after(100, dialog.attributes, '-topmost', False)
    dialog.protocol('WM_DELETE_WINDOW', on_no)

    root.mainloop()

    if not response['ans']:
        return False

    elevate_self_for_install()
    sys.exit(0)

def silent_install():
    # Check for admin rights and elevate if required
    if not is_user_admin():
        print("Elevation required. Attempting to restart as Administrator...")
        succeeded = elevate_self_for_install()
        if succeeded:
            print("UAC prompted. Exiting original process.")
            sys.exit(0)
        else:
            print("Could not elevate or UAC was declined.")
            return

    src = Path(ASSETS_DIR / 'lib/hidapi.dll')
    dest = Path(os.environ['WINDIR']) / 'System32' / 'hidapi.dll'
    try:
        shutil.copy(src, dest)
        print("hidapi.dll copied to System32 successfully.")

        # Show a confirmation popup
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Copy Successful", "hidapi.dll was copied to System32. Please restart the application.")
        root.destroy()

        sys.exit(0)
    except Exception as e:
        print(f"Failed to copy hidapi.dll: {e}")
        sys.exit(1)