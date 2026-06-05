from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase
from dsdultra.logging import log


class ButtonSave(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Save.png'
    icon_size = 35
    border_size = 90
    full = True
    highlight_hue = 77

    def run(self):
        if not hasattr(self.page.parent, 'loadout') or self.page.parent.loadout is None:
            if self.dsd.ui.ui_bridge is None:
                log.warn('Qt UI bridge is not ready; cannot open save dialog')
                return
            self.dsd.ui.ui_bridge.save_loadout_requested.emit(self.page)

