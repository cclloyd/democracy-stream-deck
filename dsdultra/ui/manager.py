from __future__ import annotations

import os
import signal
import sys
from typing import TYPE_CHECKING

from PyQt6.QtCore import QTimer, QSocketNotifier, QObject, pyqtSignal, Qt, QUrl
from PyQt6.QtGui import QIcon, QAction, QDesktopServices
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from dsdultra import ASSETS_DIR
from dsdultra.console import show_console
from dsdultra.ui.config import ConfigWindow
from dsdultra.util import is_linux, is_frozen

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra


class DSDUltraUiBridge(QObject):
    save_loadout_requested = pyqtSignal(object)


class DSDUIManager:
    dsd: DSDUltra

    def __init__(self, dsd):
        self.dsd = dsd
        self.qt_app: QApplication | None = None
        self.tray_icon: QSystemTrayIcon | None = None
        self.ui_bridge: DSDUltraUiBridge | None = None
        self._sigint_timer: QTimer | None = None
        self._signal_rfd: int | None = None
        self._signal_wfd: int | None = None
        self._signal_notifier: QSocketNotifier | None = None

    def show_config_window(self):
        dialog = ConfigWindow(self.dsd)
        dialog.exec()

    def open_config_dir(self):
        self.dsd.config.config_dir.mkdir(parents=True, exist_ok=True)
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.dsd.config.config_dir)))

    def create_tray_icon(self):
        self.qt_app = QApplication.instance() or QApplication(sys.argv)

        self.ui_bridge = DSDUltraUiBridge()
        self.ui_bridge.save_loadout_requested.connect(
            self.dsd.loadouts.open_save_dialog,
            Qt.ConnectionType.QueuedConnection,
        )

        icon_path = ASSETS_DIR / 'icons/DSDIcon.png'
        qicon = QIcon(str(icon_path))
        self.qt_app.setWindowIcon(qicon)
        self.qt_app.setQuitOnLastWindowClosed(False)

        self.tray_icon = QSystemTrayIcon(qicon)
        self.tray_icon.setToolTip('Democracy StreamDeck')

        menu = QMenu()
        menu.setTitle('Democracy StreamDeck')
        title = QAction('Democracy StreamDeck')
        title.setEnabled(False)

        action_config = QAction('Config')
        action_config.triggered.connect(self.show_config_window)
        menu.addAction(action_config)
        action_config_dir = QAction('Open config folder')
        action_config_dir.triggered.connect(lambda _checked=False: self.open_config_dir())

        action_console = QAction('Open Console')
        action_console.triggered.connect(lambda checked=False: show_console(log_path=self.dsd.config.log_path))
        action_console.setEnabled(True if is_linux() else is_frozen())

        action_console_startup = QAction('Show Console On Startup')
        action_console_startup.setCheckable(True)
        action_console_startup.setChecked(self.dsd.config.show_console)
        action_console_startup.setEnabled(is_linux() or is_frozen())

        def set_show_console(checked: bool):
            self.dsd.config.show_console = checked
            self.dsd.config.save()

        action_console_startup.toggled.connect(set_show_console)
        menu.addAction(action_console_startup)

        action_screenshot = QAction('Take Screenshot')
        action_screenshot.triggered.connect(lambda _checked=False: self.dsd.state.screenshot())

        action_update = QAction('Check for updates')
        action_update.triggered.connect(lambda _checked=False: self.dsd.installer.check_for_updates())

        action_exit = QAction('Exit')
        action_exit.triggered.connect(self.dsd.request_shutdown)

        menu.addAction(title)
        menu.addSeparator()
        menu.addAction(action_config_dir)
        menu.addAction(action_console)
        menu.addAction(action_screenshot)
        menu.addAction(action_update)
        menu.addAction(action_exit)

        self.tray_icon.setContextMenu(menu)
        self.tray_icon.show()

        # Ensure SIGINT/SIGTERM reliably wakes Qt's event loop on Unix.
        # This makes Ctrl+C work even while QApplication.exec() is running.
        try:
            self._signal_rfd, self._signal_wfd = os.pipe()
            os.set_blocking(self._signal_rfd, False)
            os.set_blocking(self._signal_wfd, False)
            signal.set_wakeup_fd(self._signal_wfd)

            self._signal_notifier = QSocketNotifier(self._signal_rfd, QSocketNotifier.Type.Read, self.qt_app)

            def _on_signal_ready():
                try:
                    os.read(self._signal_rfd, 4096)
                except OSError:
                    pass
                self.dsd.request_shutdown()

            self._signal_notifier.activated.connect(_on_signal_ready)
        except Exception:
            # Fallback: keep a tiny timer so Python regains control periodically.
            self._sigint_timer = QTimer()
            self._sigint_timer.setInterval(200)
            self._sigint_timer.timeout.connect(lambda: None)
            self._sigint_timer.start()

        try:
            self.qt_app.exec()
        finally:
            # Best-effort cleanup
            try:
                if self._signal_notifier is not None:
                    self._signal_notifier.setEnabled(False)
            except Exception:
                pass
            try:
                if self._signal_rfd is not None:
                    os.close(self._signal_rfd)
            except Exception:
                pass
            try:
                if self._signal_wfd is not None:
                    os.close(self._signal_wfd)
            except Exception:
                pass