from dsdultra.buttons.base import ButtonBase


class ButtonExit(ButtonBase):
    icon = 'dsdultra/assets/icons/groups/Close.png'
    icon_size = 35
    border_size = 90
    color = 'yellow'
    full = True
    gild = True

    def __init__(self, dsd, page=None, config=None):
        super().__init__(dsd, page=page, config=None)
