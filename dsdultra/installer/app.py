from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse
from urllib.request import urlretrieve

import requests
from packaging.version import Version
from platformdirs import user_downloads_dir
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from dsdultra.version import VERSION
from dsdultra.util import is_windows

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra


def normalize_version(version: str) -> Version:
    return Version(version.removeprefix('v'))


class UpdateDialog(QDialog):
    def __init__(self, installer: DSDInstaller, parent=None):
        super().__init__(parent)

        self.installer = installer

        self.setWindowTitle('Democracy StreamDeck')
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        if installer.latest_version is None:
            layout.addWidget(QLabel('No update was found.'))

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(self.accept)
            layout.addWidget(buttons)

            return

        if not installer.update_available:
            layout.addWidget(QLabel('You are already using the most up to date version.'))

            form = QFormLayout()
            form.addRow('Current version:', QLabel(str(VERSION)))
            form.addRow('Latest version:', QLabel(str(installer.latest_version)))
            layout.addLayout(form)

            buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
            buttons.accepted.connect(self.accept)
            layout.addWidget(buttons)

            return

        layout.addWidget(QLabel('An update is available.'))

        form = QFormLayout()
        form.addRow('Current version:', QLabel(str(VERSION)))
        form.addRow('New version:', QLabel(str(installer.latest_version)))
        layout.addLayout(form)

        self.download_button = QPushButton('Download Update')
        self.download_button.clicked.connect(self.download_update)
        layout.addWidget(self.download_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def download_update(self):
        self.download_button.setEnabled(False)
        self.download_button.setText('Downloading update...')
        try:
            destination = self.installer.update()
            QMessageBox.information(
                self,
                'Update Downloaded',
                f'The update was downloaded to:\n\n{destination}\n\nThe program will now close.',
            )
            self.accept()
            sys.exit(0)
        except Exception as e:
            self.download_button.setEnabled(True)
            self.download_button.setText('Download Update')
            QMessageBox.critical(
                self,
                'Download Failed',
                f'Failed to download the update:\n\n{e}',
            )


class DSDInstaller:
    dsd: DSDUltra
    update_available: bool = False
    latest_version: str | None = None

    def __init__(self, dsd: DSDUltra):
        self.dsd = dsd

    def check_for_updates(self) -> bool:
        url = 'https://github.com/cclloyd/democracy-stream-deck/releases/latest'
        semver = None

        try:
            print('Checking for updates...')
            if VERSION.startswith('dev'):
                self.update_available = False
                self.latest_version = None
                return self.update_available

            response = requests.get(url, allow_redirects=True, timeout=10)
            response.raise_for_status()

            path_parts = urlparse(response.url).path.rstrip('/').split('/')

            if 'tag' in path_parts:
                tag_index = path_parts.index('tag')
                semver = path_parts[tag_index + 1]

            self.latest_version = semver
            self.update_available = (normalize_version(semver) > normalize_version(VERSION) if semver else False)
            print(f'Update found: {self.latest_version}')
            self.show_update_dialog()
        except Exception as e:
            print(f'Failed to check for updates: {e}')
            self.update_available = False
            self.latest_version = None

    def show_update_dialog(self, parent=None):
        dialog = UpdateDialog(self, parent)
        dialog.exec()

    def update(self) -> Path:
        if is_windows():
            url = 'https://github.com/cclloyd/democracy-stream-deck/releases/latest/download/dsd.exe'
        else:
            url = 'https://github.com/cclloyd/democracy-stream-deck/releases/latest/download/dsd.AppImage'

        exe = Path(sys.argv[0]).resolve()
        downloads_dir = Path(user_downloads_dir())
        downloads_dir.mkdir(parents=True, exist_ok=True)

        filename = url.split('/')[-1] if exe.name.endswith('.py') else exe.name
        destination = downloads_dir / filename
        urlretrieve(url, destination)

        if not is_windows():
            destination.chmod(0o755)

        print(f'Downloaded update to: {destination}')

        return destination