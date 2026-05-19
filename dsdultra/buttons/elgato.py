import subprocess
import threading
from pathlib import WindowsPath

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase


class ButtonElgato(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/groups/elgato.png'
    color = 'none'
    icon_size = 65
    border_size = 90
    full = True
    toggle_id = 'elgato'
    highlight_hue = 210

    def run(self):
        if self.page.toggle_active.get('elgato', False):
            elgato_path = WindowsPath('C:\\Program Files\\Elgato\\StreamDeck\\StreamDeck.exe')
            subprocess.Popen([str(elgato_path)], close_fds=True)
            self.shutdown()
        else:
            self.page.toggle_active['elgato'] = True
            self.page.render(True)

            # Automatically reset the toggle after 3 seconds
            def _reset():
                # Only reset if still active
                if self.page.toggle_active.get('elgato', False):
                    self.page.toggle_active['elgato'] = False
                    # Re-render to clear highlight
                    try:
                        self.page.render(True)
                    except Exception:
                        pass

            t = threading.Timer(self.toggle_timeout, _reset)
            t.daemon = True
            t.start()

