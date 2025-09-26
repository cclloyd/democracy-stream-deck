from dsdultra.buttons.base import ButtonBase
from dsdultra import ASSETS_DIR


class ButtonHome(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = ASSETS_DIR / 'icons/borders/SE.png'
    color = 'rainbow'
    # icon = ASSETS_DIR / 'icons/borders/SE.png'
    # color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True

    def run(self):
        self.page.app.close()
        self.dsd.apps.get('dsd').render(True)
