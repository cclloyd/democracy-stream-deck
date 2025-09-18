from dsdultra.buttons.base import ButtonBase
from dsdultra.pages.armory import PageArmory


class ButtonArmory(ButtonBase):
    def __init__(self, dsd, page=None):
        super().__init__(dsd, page=page)

    icon = 'dsdultra/assets/icons/groups/Armory.png'
    icon_size = 45
    border_size = 90
    color = 'rainbow'
    full = True

    def run(self):
        page = PageArmory(self.dsd, parent=self.page, app='armory')
        page.render()
