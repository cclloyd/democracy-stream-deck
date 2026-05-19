import os
import json
from pathlib import Path, WindowsPath
from collections.abc import MutableMapping

class DSDConfig(MutableMapping):
    dsd = None
    if os.name != 'nt':
        appdata = Path.home() / '.config' / 'dsd'
    else:
        appdata = os.environ['APPDATA']
    config_path = Path(appdata) / 'dsd' / 'dsd-config.json'

    obs_host = None
    obs_port = None
    obs_password = None
    elgato_path = WindowsPath('C:\\Program Files\\Elgato\\StreamDeck\\StreamDeck.exe')
    loadout_path = Path(appdata) / 'dsd' / 'loadouts.json'

    def __init__(self, dsd):
        self.dsd = dsd
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                self.elgato_path = self.config.get('elgato_path', self.elgato_path)
                self.obs_host = self.config.get('obs_host', self.obs_host)
                self.obs_port = self.config.get('obs_port', self.obs_port)
                self.obs_password = self.config.get('obs_password', self.obs_password)
        else:
            self.config = dict()

    def __getitem__(self, key):
        return self.config[key]

    def __setitem__(self, key, value):
        self.config[key] = value

    def __delitem__(self, key):
        del self.config[key]

    def __iter__(self):
        return iter(self.config)

    def __len__(self):
        return len(self.config)

    def get(self, key, default=None):
        return self.config.get(key, default)