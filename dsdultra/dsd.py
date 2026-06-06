import threading
from argparse import Namespace
from pathlib import Path

from StreamDeck.Devices.StreamDeck import StreamDeck as StreamDeckDevice

from dsdultra.armory.loadouts import Loadouts
from dsdultra.armory.stratagems import Stratagem
from dsdultra.armory.superdestroyer import SuperDestroyer
from dsdultra.config import DSDConfig
from dsdultra.icons import IconGenerator
from dsdultra.installer.app import DSDInstaller
from dsdultra.obs import OBS
from dsdultra.pages.home import PageHome
from dsdultra.state import StateManager
from dsdultra.ui.manager import DSDUIManager


class DSDUltra:
    config: DSDConfig = None
    deck: StreamDeckDevice = None
    icons: IconGenerator = None
    apps: dict = dict()

    def __init__(self, deck, args: Namespace, started=None, config=None):
        self.ASSET_DIR = Path(__file__).parent / 'assets'
        self.args = args
        self.started = config.started if config else started
        self.config = config or DSDConfig(self)
        if config:
            self.config.dsd = self
        self.deck: StreamDeckDevice = deck
        self.stop_event = threading.Event()
        self.icons = IconGenerator(self)
        self.obs = OBS(self)
        self.state = StateManager(self)
        self.stratagems = Stratagem.load_stratagems()
        self.armory = SuperDestroyer(self)
        self.loadouts = Loadouts(self)
        self.ui = DSDUIManager(self)
        self.installer = DSDInstaller(self)

    def start(self):
        deck_thread = threading.Thread(target=self._deck_loop, name='StreamDeckThread', daemon=True)
        deck_thread.start()
        print('Started streamdeck thread')
        self.ui.create_tray_icon()
        print('Created tray icon')

    def _deck_loop(self):
        self.deck.open()
        self.deck.reset()
        print(f'Opened: {self.deck.deck_type()}  SN: {self.deck.get_serial_number()}  FW: {self.deck.get_firmware_version()}')

        self.deck.set_brightness(50)
        initial_page = PageHome(self, app='dsd')
        initial_page.render()

        while self.deck.is_open() and not self.stop_event.is_set():
            self.stop_event.wait(0.1)

        try:
            if self.deck.is_open():
                self.deck.reset()
                self.deck.close()
        except Exception as e:
            print(f'Error closing deck: {e}')

    def shutdown(self, code=0):
        print('Shutting down...')
        self.request_shutdown()

    def request_shutdown(self):
        self.stop_event.set()
        try:
            if self.deck is not None and self.deck.is_open():
                self.deck.reset()
                self.deck.close()
                print('Deck closed')
        except Exception as e:
            print(f'Error closing deck: {e}')

        try:
            if self.ui.tray_icon is not None:
                self.ui.tray_icon.hide()
                print('Removed tray icon')
        except Exception:
            pass

        if self.ui.qt_app is not None:
            self.ui.qt_app.quit()
