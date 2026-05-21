import threading

from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR


class ButtonExit(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 35
    border_size = 90
    color = 'rainbow'
    full = True
    gild = True

    def __init__(self, dsd, page=None, config=None):
        super().__init__(dsd, page=page, config=None)

    def run(self):
       self.shutdown()

class ButtonExitConfirm(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 35
    border_size = 90
    color = 'rainbow'
    full = True
    gild = True
    toggle_id = 'exit'
    highlight_hue = 320
    toggle_timeout = 2

    def run(self):
        if self.page.is_highlight_active(self.toggle_id):
           self.shutdown()
        else:
            self.page.set_highlight(self.toggle_id, True)

            def _reset():
                # Only reset if still active
                if self.page.is_highlight_active(self.toggle_id):
                    self.page.set_highlight(self.toggle_id, False)

            t = threading.Timer(self.toggle_timeout, _reset)
            t.daemon = True
            t.start()

