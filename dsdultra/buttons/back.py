from dsdultra import ASSETS_DIR
from dsdultra.buttons.base import ButtonBase


class ButtonBack(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/groups/Arrow.png'
    icon_size = 35
    icon_rotate = 180
    border_size = 90
    color = 'yellow'
    full = True
    gild = True

    def run(self):
        if self.page.parent:
            self.page.parent.render(True)
