import ctypes
import os
import shutil
import sys
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

from dsdultra import ASSETS_DIR


class WindowsInstallerWizard:
    def is_user_admin(self):
        """Check if the user has admin privileges on Windows."""
        try:
            return ctypes.windll.shell32.IsUserAnAdmin()
        except Exception:
            return False

    def elevate_self_for_install(self):
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

    def prompt_library_install(self):

        app = QApplication.instance() or QApplication(sys.argv)

        dialog = QDialog()
        dialog.setWindowTitle('Missing hidapi.dll')
        dialog.setModal(True)
        dialog.setFixedSize(480, 240)

        layout = QVBoxLayout(dialog)

        msg = (
            'hidapi.dll is missing (No suitable LibUSB driver in any PATH directory).\n\n'
            'Would you like to install \'hidapi.dll\' to your System32 folder?\n'
        )

        message_label = QLabel(msg)
        message_label.setWordWrap(True)
        layout.addWidget(message_label)

        link = QLabel('<a href="https://github.com/libusb/hidapi/releases">View/download hidapi releases</a>')
        link.setTextFormat(Qt.TextFormat.RichText)
        link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        link.setOpenExternalLinks(False)
        link.linkActivated.connect(lambda url: QDesktopServices.openUrl(QUrl(url)))
        layout.addWidget(link)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() != QDialog.DialogCode.Accepted:
            return False

        self.elevate_self_for_install()
        sys.exit(0)

    def silent_install(self):
        # Check for admin rights and elevate if required
        if not self.is_user_admin():
            print("Elevation required. Attempting to restart as Administrator...")
            succeeded = self.elevate_self_for_install()
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

            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.information(
                None,
                "Copy Successful",
                "hidapi.dll was copied to System32. Please restart the application.",
            )

            sys.exit(0)
        except Exception as e:
            print(f"Failed to copy hidapi.dll: {e}")
            sys.exit(1)
