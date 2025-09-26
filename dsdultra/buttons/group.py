from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR


class ButtonGroup(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Armory.png'
    icon_size = 45
    border_size = 90
    color = 'rainbow'
    full = True

