import json
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra
from dsdultra.pages.quick import PageQuickInfo
from dsdultra.ui.loadout import LoadoutSaveWindow


class Loadouts:
    loadouts = []

    def __init__(self, dsd):
        self.dsd: DSDUltra = dsd
        self.loadouts = []
        if self.dsd.config.loadout_path.exists():
            with open(self.dsd.config.loadout_path, 'r') as f:
                for line in f:
                    self.loadouts.append(Loadout(**json.loads(line)))

    def save_loadout(self, config, overwrite=False):
        try:
            self.dsd.config.loadout_path.parent.mkdir(parents=True, exist_ok=True)

            existing_configs = []
            existing_index = None

            if self.dsd.config.loadout_path.exists():
                with open(self.dsd.config.loadout_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue

                        existing_config = json.loads(line)
                        if existing_config.get('id') == config.get('id'):
                            existing_index = len(existing_configs)

                        existing_configs.append(existing_config)

            if existing_index is not None and not overwrite:
                return False

            if existing_index is None:
                existing_configs.append(config)
            else:
                existing_configs[existing_index] = config

            with open(self.dsd.config.loadout_path, 'w') as f:
                for existing_config in existing_configs:
                    f.write(json.dumps(existing_config) + '\n')

            self.loadouts = [Loadout(**existing_config) for existing_config in existing_configs]
            return True
        except Exception as e:
            print(e)
            traceback.print_exc()
            raise e

    def open_save_dialog(self, page: PageQuickInfo):
        stratagems = []
        for item in page.content:
            config = item.config if hasattr(item, 'config') else item
            stratagem_id = config.get('id') if isinstance(config, dict) else getattr(item, 'id', None)
            if stratagem_id:
                stratagems.append(stratagem_id)

        data = {
            'id': 'new_loadout',
            'name': 'New Loadout',
            'stratagems': stratagems,
        }

        dialog = LoadoutSaveWindow(self.dsd, data)
        dialog.exec()


class Loadout:
    icon1 = None
    icon2 = None
    icon3 = None
    icon4 = None
    id = None
    name = None
    hint = None
    stratagems = None

    def __init__(self, icon1=None, icon2=None, icon3=None, icon4=None, id=None, name=None, hint=None, stratagems=None):
        self.icon1 = icon1
        self.icon2 = icon2
        self.icon3 = icon3
        self.icon4 = icon4
        self.id = id
        self.name = name
        self.hint = hint
        self.stratagems = stratagems or []

    @property
    def config(self):
        # Backwards compatible function with to-be-replaced button.config option
        config = dict(self.__dict__)
        return config