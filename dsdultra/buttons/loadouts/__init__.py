from dsdultra.buttons.base import ButtonBase
from dsdultra.pages.loadouts import PageLoadouts


class ButtonLoadouts(ButtonBase):
    icon = 'dsdultra/assets/icons/groups/Factions.png'
    icon_size = 55
    border_size = 90
    color = 'rainbow'
    full = True

    def run(self):
        page = PageLoadouts(self.dsd, parent=self.page, app='quick')
        page.render()
