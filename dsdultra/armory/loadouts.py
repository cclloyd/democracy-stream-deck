from __future__ import annotations

import json
import traceback
from typing import TYPE_CHECKING

from dsdultra.armory.stratagems import Stratagem
from dsdultra.buttons.stratagem import ButtonStratagem
from dsdultra.pages.loadouts import PageLoadouts

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra
from dsdultra.pages.quick import PageQuickInfo
from dsdultra.ui.loadout import LoadoutSaveWindow


class Loadouts:
    loadouts = []
    unsaved: 'Loadout'

    def __init__(self, dsd):
        self.dsd: DSDUltra = dsd
        self.loadouts = []
        self.save_dialog = None
        if self.dsd.config.loadout_path.exists():
            with open(self.dsd.config.loadout_path, 'r') as f:
                self.loadouts = [Loadout(self.dsd, **config) for config in json.load(f)]
        self.unsaved = Loadout(self.dsd)

    def get_loadout(self, loadout_id, load_from_file=False):
        if load_from_file:
            with open(self.dsd.config.loadout_path, 'r') as f:
                for config in json.load(f):
                    if config['id'] == loadout_id:
                        return Loadout(self.dsd, **config)
            return None
        for loadout in self.loadouts:
            if loadout.id == loadout_id:
                return loadout
        return None

    # TODO: Make save button save open loadout window without confirmation (or confirm on double-press)
    def save_loadout(self, config, overwrite=False):
        try:
            self.dsd.config.loadout_path.parent.mkdir(parents=True, exist_ok=True)

            existing_configs = []
            existing_index = None

            if self.dsd.config.loadout_path.exists():
                with open(self.dsd.config.loadout_path, 'r') as f:
                    existing_configs = json.load(f)

                for index, existing_config in enumerate(existing_configs):
                    if existing_config.get('id') == config.get('id'):
                        existing_index = index
                        break

            if existing_index is not None and not overwrite:
                return False

            if existing_index is None:
                existing_configs.append(config)
            else:
                existing_configs[existing_index] = config

            with open(self.dsd.config.loadout_path, 'w') as f:
                json.dump(existing_configs, f, default=str, indent=2)

            self.loadouts = [Loadout(self.dsd, **existing_config) for existing_config in existing_configs]
            app = self.dsd.state.apps.get('loadouts', None)
            if app:
                app.refresh()
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

    def delete_loadout(self, loadout_id):
        try:
            self.dsd.config.loadout_path.parent.mkdir(parents=True, exist_ok=True)

            existing_configs = []
            new_configs = []

            if self.dsd.config.loadout_path.exists():
                with open(self.dsd.config.loadout_path, 'r') as f:
                    existing_configs = json.load(f)
                new_configs = [c for c in existing_configs if c.get('id') != loadout_id]

            with open(self.dsd.config.loadout_path, 'w') as f:
                json.dump(new_configs, f, default=str, indent=2)

            self.loadouts = [Loadout(self.dsd, **c) for c in new_configs]
            app = self.dsd.state.apps.get('loadouts', None)
            if app:
                app.refresh()
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

    def open_save_dialog(self, page: PageQuickInfo):
        try:
            stratagems = []
            for item in page.content:
                config = item.config if hasattr(item, 'config') else item
                stratagem_id = config.get('id') if isinstance(config, dict) else getattr(item, 'id', None)
                if stratagem_id:
                    stratagems.append(stratagem_id)
            if isinstance(page.app, PageLoadouts):
                stratagems = page.parent.loadout.stratagems
            else:
                strategem_ids = []
                for item in page.content:
                    config = item.config if hasattr(item, 'config') else item
                    stratagem_id = config.get('id') if isinstance(config, dict) else getattr(item, 'id', None)
                    if stratagem_id:
                        strategem_ids.append(stratagem_id)
                stratagems = Stratagem.parse_stratagems(self.dsd, strategem_ids)

            if self.save_dialog is not None and self.save_dialog.isVisible():
                self.save_dialog.data['stratagems'] = stratagems
                self.save_dialog.save(overwrite=True)
                self.save_dialog = None
                return

            loadout = page.parent.loadout if isinstance(page.app, PageLoadouts) else Loadout(self.dsd, stratagems=stratagems, new=True)
            self.save_dialog = LoadoutSaveWindow(self.dsd, loadout)
            self.save_dialog.finished.connect(lambda: setattr(self, 'save_dialog', None))
            self.save_dialog.exec()
        except Exception as e:
            print(f"Error opening save dialog: {e}")
            traceback.print_exc()
            raise e


class Loadout:
    icon1 = None
    icon2 = None
    icon3 = None
    icon4 = None
    id = None
    name = None
    hint = None
    color = 'yellow'
    full = True
    stratagems = None

    def __init__(self, dsd=None, icon1=None, icon2=None, icon3=None, icon4=None, id='new_loadout', name='New Loadout', hint=None, stratagems=None, color='yellow', full=True, new=False):
        self.dsd = dsd
        self.icon1 = icon1
        self.icon2 = icon2
        self.icon3 = icon3
        self.icon4 = icon4
        self.id = id
        self.name = name
        self.hint = hint
        self.color = color
        self.full = full
        self.set_stratagems(dsd, stratagems or [])
        if new:
            self.name = f'New Loadout ({len(dsd.loadouts.loadouts) + 1})'
            self.id = f'new_loadout{len(dsd.loadouts.loadouts) + 1}'

    @property
    def config(self):
        # Backwards compatible function with to-be-replaced button.config option
        config = dict(self.__dict__)
        config['stratagems'] = self.stratagems
        # Remove unwanted attributes
        config.pop('dsd', None)
        return config

    def set_stratagems(self, dsd: DSDUltra, stratagems: list[str | Stratagem]) -> list[Stratagem]:
        filtered = []
        for s in stratagems:
            if isinstance(s, Stratagem):
                filtered.append(s)
            elif isinstance(s, ButtonStratagem):
                filtered.append(dsd.armory.all[s.config['id']])
            else:
                filtered.append(dsd.armory.all[s])
        self.stratagems = filtered

    def __str__(self):
        return f'<Loadout:{self.id}:{self.color}:{",".join([s.id for s in self.stratagems])}>'

    def __repr__(self):
        return str(self)
