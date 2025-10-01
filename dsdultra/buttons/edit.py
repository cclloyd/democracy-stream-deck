from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase


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
            self.page.select_active = 'swap'
            self.page.selected = []
            self.page.render(True)
        else:
            self.page.toggle_active['swap'] = True
            self.page.select_active = 'swap'
            self.page.render(True)


class ButtonRemove(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 30
    border_size = 90
    color = 'yellow'
    full = True
    toggle_id = 'remove'
    highlight_hue = 77

    # TODO: design pattern is backwards.  We should have the toggled button trigger a run command on this class, sending itself as a parameter.
    def run(self):
        if self.page.select_active == 'remove':
            self.page.toggle_active['remove'] = False
            self.page.select_active = None
            self.page.selected = []
            self.page.render(True)
        else:
            self.page.toggle_active['remove'] = True
            self.page.select_active = 'remove'
            self.page.render(True)