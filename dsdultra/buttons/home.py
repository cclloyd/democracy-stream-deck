from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR
import threading


class ButtonHome(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/borders/SE.png'
    color = 'rainbow'
    # icon = ASSETS_DIR / 'icons/borders/SE.png'
    # color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True

    def run(self):
        self.page.app.close()
        self.dsd.apps.get('dsd').render(True)


class ButtonHomeConfirm(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/borders/SE.png'
    color = 'rainbow'
    # icon = ASSETS_DIR / 'icons/borders/SE.png'
    # color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True
    toggle_id = 'home'
    highlight_hue = 320

    def run(self):
        if self.page.toggle_active.get('home', False):
            self.page.app.close()
            self.dsd.apps.get('dsd').render(True)
        else:
            self.page.toggle_active['home'] = True
            self.page.render(True)

            # Automatically reset the toggle after 3 seconds
            def _reset():
                # Only reset if still active
                if self.page.toggle_active.get('home', False):
                    self.page.toggle_active['home'] = False
                    # Re-render to clear highlight
                    try:
                        self.page.render(True)
                    except Exception:
                        pass

            t = threading.Timer(5, _reset)
            t.daemon = True
            t.start()
