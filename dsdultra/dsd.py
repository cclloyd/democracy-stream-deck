import io
import os
import signal
import sys
import threading

from PIL import Image
from StreamDeck.Devices.StreamDeck import StreamDeck as StreamDeckDevice
from pystray import MenuItem, Menu, Icon

from dsdultra.config import DSDConfig
from dsdultra.icons import IconGenerator
from dsdultra.pages.home import PageHome


class DSDUltra:
    config: DSDConfig = None
    deck: StreamDeckDevice = None
    icons: IconGenerator = None
    apps: dict = dict()

    def __init__(self, deck):
        self.deck: StreamDeckDevice = deck
        self.icons = IconGenerator(self)
        self.BUTTON_SIZE = 72

    def start(self):
        self.config = DSDConfig(self)
        self.create_tray_icon()
        self.deck.open()
        self.deck.reset()
        self.BUTTON_SIZE = self.deck.KEY_PIXEL_WIDTH
        print(f'Opened: {self.deck.deck_type()}  SN: {self.deck.get_serial_number()}  FW: {self.deck.get_firmware_version()}')

        self.deck.set_brightness(50)
        initial_page = PageHome(self, app='dsd')
        initial_page.render()

        current = threading.current_thread()
        while self.deck.is_open():
            for t in threading.enumerate():
                if t is current:
                    continue
                try:
                    t.join(timeout=1)
                except RuntimeError as e:
                    print(e)
                    pass

    def create_tray_icon(self):
        def on_exit(tray_icon, item):
            tray_icon.stop()
            self.deck.reset()
            self.deck.close()

        def run_tray():
            image_path = 'dsdultra/assets/icons/DSDIcon.png'
            icon_image = Image.open(image_path)
            menu = Menu(
                MenuItem("Democracy StreamDeck", None, enabled=False),
                MenuItem('Exit', on_exit),
            )
            icon = Icon('dsd', icon_image, 'Democracy StreamDeck', menu)
            icon.run()

        tray_thread = threading.Thread(target=run_tray, name='TrayIconThread', daemon=True)
        tray_thread.start()

    def set_image(self, key, img):
        if key >= self.deck.key_count():
            return  # touch strip on SD+ is beyond key indexes
        self.deck.set_key_image(key, img)


