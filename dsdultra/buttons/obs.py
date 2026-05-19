import threading

from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase


class ButtonRecord(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)
        if self.page.toggle_active.get('obs', False) == 'error':
            self.highlight_hue = 310

    icon = ASSETS_DIR / 'icons/groups/OBS.png'
    color = 'none'
    icon_size = 70
    border_size = 90
    full = True
    toggle_id = 'obs'
    highlight_hue = 77
    toggle_timeout = 3

    def run(self):
        # Automatically reset the toggle after 3 seconds
        def _reset():
            # Only reset if still active
            if self.page.toggle_active.get('obs', False):
                self.page.toggle_active['obs'] = False
                # Re-render to clear highlight
                try:
                    self.page.render(True)
                except Exception:
                    pass

        t = threading.Timer(self.toggle_timeout, _reset)
        t.daemon = True
        try:
            self.dsd.obs.record()
        except:
            self.page.toggle_active['obs'] = 'error'
            self.highlight_hue = 310
        t.start()
        if not self.page.toggle_active.get('obs', False):
            self.page.toggle_active['obs'] = True
        self.page.render(True)