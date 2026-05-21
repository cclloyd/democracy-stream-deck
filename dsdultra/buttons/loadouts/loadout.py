from dsdultra import ASSETS_DIR
from dsdultra.armory.stratagems import Stratagem
from dsdultra.buttons.base import ButtonBase


class ButtonLoadout(ButtonBase):
    icon = None
    icon_size = 60
    border_size = 90
    full = True

    def __init__(self, dsd, *args, **kwargs):
        super().__init__(dsd, *args, **kwargs)

    def run(self):
        from dsdultra.pages.quick import PageQuickLoadout
        stratagems = Stratagem.parse_stratagems(self.dsd, self.config.get('stratagems', []))
        loadout = self.dsd.loadouts.get_loadout(self.config['id'])
        self.page.set_select('stratagems', stratagems)
        self.page.set_store('active_loadout', loadout, rerender=False)
        page = PageQuickLoadout(self.dsd, parent=self.page, content=stratagems, loadout=loadout)
        page.render(True)


class ButtonRefreshLoadout(ButtonBase):
    icon = ASSETS_DIR / 'icons/groups/Reload.png'
    icon_size = 35
    border_size = 90
    full = True

    def run(self):
        loadout = self.dsd.loadouts.get_loadout(self.page.get_store('active_loadout').id, load_from_file=True)
        self.page.set_store('active_loadout', loadout, rerender=True)
        self.page.set_select('stratagems', [*loadout.stratagems])

    def should_render(self):
        return self.page.get_store('active_loadout') is not None and self.page.get_store('active_loadout').id != 'new_loadout'
