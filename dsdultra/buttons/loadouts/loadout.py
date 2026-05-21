from dsdultra.armory.stratagems import Stratagem
from dsdultra.buttons.base import ButtonBase


class ButtonLoadout(ButtonBase):
    icon = None
    icon_size = 60
    border_size = 90
    full = True

    def run(self):
        from dsdultra.pages.quick import PageQuickLoadout
        parent = self.page
        # TODO: Need to pass buttons instead of config dict to selection
        self.page.add_select('stratagems', self.config)
        page = PageQuickLoadout(self.dsd, parent=parent, config=self.config, content=Stratagem.parse_stratagems(self.dsd, self.config.get('stratagems', [])))
        page.render(True)
