from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase
from dsdultra.logging import log


class ButtonSwap(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Swap.png'
    icon_size = 50
    border_size = 90
    full = True
    toggle_id = 'swap'
    highlight_hue = 77

    def run(self):
        self.page.toggle_select(self.toggle_id)
        self.page.toggle_highlight(self.toggle_id)


class ButtonRemove(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 30
    border_size = 90
    full = True
    toggle_id = 'remove'

    def run(self):
        self.page.toggle_select(self.toggle_id, rerender=False)
        self.page.toggle_highlight(self.toggle_id)


class ButtonEdit(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Edit.png'
    icon_size = 35
    border_size = 90
    full = True

    def run(self):
        if self.dsd.ui.ui_bridge is None:
            log.warn('Qt UI bridge is not ready; cannot open save dialog')
            return
        self.dsd.ui.ui_bridge.save_loadout_requested.emit(self.page)
