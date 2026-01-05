import sys
import threading
from argparse import Namespace
import os
import signal

from PyQt6.QtCore import QTimer, QSocketNotifier
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
from StreamDeck.Devices.StreamDeck import StreamDeck as StreamDeckDevice

from dsdultra import ASSETS_DIR
from dsdultra.config import DSDConfig
from dsdultra.console import show_console
from dsdultra.icons import IconGenerator
from dsdultra.obs import OBS
from dsdultra.pages.home import PageHome
from dsdultra.util import is_frozen


class DSDUltra:
    config: DSDConfig = None
    deck: StreamDeckDevice = None
    icons: IconGenerator = None
    apps: dict = dict()

    def __init__(self, deck, args: Namespace):
        self.deck: StreamDeckDevice = deck
        self.tray: threading.Thread | None = None
        self.stop_event = threading.Event()
        self.args = args
        self.icons = IconGenerator(self)
        self.obs = OBS(self)
        self.BUTTON_SIZE = 72

        self.qt_app: QApplication | None = None
        self.tray_icon: QSystemTrayIcon | None = None
        self._sigint_timer: QTimer | None = None

        self._signal_rfd: int | None = None
        self._signal_wfd: int | None = None
        self._signal_notifier: QSocketNotifier | None = None

    def start(self):
        self.config = DSDConfig(self)
        deck_thread = threading.Thread(target=self._deck_loop, name='StreamDeckThread', daemon=True)
        deck_thread.start()
        self.create_tray_icon()

    def _deck_loop(self):
        self.deck.open()
        self.deck.reset()
        self.BUTTON_SIZE = self.deck.KEY_PIXEL_WIDTH
        print(f'Opened: {self.deck.deck_type()}  SN: {self.deck.get_serial_number()}  FW: {self.deck.get_firmware_version()}')

        self.deck.set_brightness(50)
        initial_page = PageHome(self, app='dsd')
        initial_page.render()

        while self.deck.is_open() and not self.stop_event.is_set():
            self.stop_event.wait(0.25)

        try:
            if self.deck.is_open():
                self.deck.reset()
                self.deck.close()
        except Exception as e:
            print(f'Error closing deck: {e}')

    def _request_shutdown(self):
        self.stop_event.set()

        try:
            if self.deck is not None and self.deck.is_open():
                self.deck.reset()
                self.deck.close()
        except Exception as e:
            print(f'Error closing deck: {e}')

        try:
            if self.tray_icon is not None:
                self.tray_icon.hide()
        except Exception:
            pass

        if self.qt_app is not None:
            self.qt_app.quit()

    def create_tray_icon(self):
        self.qt_app = QApplication.instance() or QApplication(sys.argv)

        icon_path = ASSETS_DIR / 'icons/DSDIcon.png'
        qicon = QIcon(str(icon_path))

        self.tray_icon = QSystemTrayIcon(qicon)
        self.tray_icon.setToolTip('Democracy StreamDeck')

        menu = QMenu()
        menu.setTitle('Democracy StreamDeck')
        title = QAction('Democracy StreamDeck')
        title.setEnabled(False)
        menu.addAction(title)
        menu.addSeparator()

        action_console = QAction('Show Console')
        action_console.triggered.connect(show_console)
        action_console.setEnabled(is_frozen())
        menu.addAction(action_console)

        action_exit = QAction('Exit')
        action_exit.triggered.connect(self._request_shutdown)
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
                self._request_shutdown()

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

    def set_image(self, key, img):
        if key >= self.deck.key_count():
            return  # touch strip on SD+ is beyond key indexes
        self.deck.set_key_image(key, img)

    def shutdown(self, code=0):
        print('Shutting down...')
        return self._request_shutdown()
