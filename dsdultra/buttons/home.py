from dsdultra.buttons.base import ButtonBase


class ButtonHome(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = 'dsdultra/assets/icons/borders/SE.png'
    color = 'rainbow'
    # icon = 'dsdultra/assets/icons/borders/SE.png'
    # color = 'rainbow'
    icon_size = 50
    border_size = 90
    full = True
    gild = True

    def run(self):
        self.page.app.close()
        self.dsd.apps.get('dsd').render(True)
