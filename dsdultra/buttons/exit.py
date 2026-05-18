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
        if self.page.toggle_active.get('exit', False):
           self.shutdown()
        else:
            self.page.toggle_active['exit'] = True
            self.page.render(True)

            # Automatically reset the toggle after 3 seconds
            def _reset():
                # Only reset if still active
                if self.page.toggle_active.get('exit', False):
                    self.page.toggle_active['exit'] = False
                    # Re-render to clear highlight
                    try:
                        self.page.render(True)
                    except Exception:
                        pass

            t = threading.Timer(self.toggle_timeout, _reset)
            t.daemon = True
            t.start()

