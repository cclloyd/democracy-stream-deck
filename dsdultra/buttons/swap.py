from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase

try:
    from pynput.keyboard import Controller as _KbController
    from pynput.keyboard import Key as _KbKey
    _kb = _KbController()
except Exception:
    print('WARNING: No keyboard input available.')
    _kb = None


class ButtonSwap(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Swap.png'
    icon_size = 50
    border_size = 90
    color = 'yellow'
    full = True
    toggle_id = 'swap'
    highlight_hue = 77

    def run(self):
        if self.page.select_active:
            self.page.toggle_active['swap'] = False
            self.page.select_active = False
            self.page.selected = []
            self.page.render(True)
        else:
            self.page.toggle_active['swap'] = True
            self.page.select_active = True
            self.page.render(True)