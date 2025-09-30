from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase


class ButtonRecord(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/groups/OBS.png'
    color = 'none'
    icon_size = 70
    border_size = 90
    full = True

    def run(self):
        pass
        self.dsd.obs.record()
