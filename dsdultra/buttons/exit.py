from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR


class ButtonExit(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Close.png'
    icon_size = 35
    border_size = 90
    color = 'yellow'
    full = True
    gild = True

    def __init__(self, dsd, page=None, config=None):
        super().__init__(dsd, page=page, config=None)
