import os
import json
from pathlib import Path, WindowsPath
from collections.abc import MutableMapping

unix = os.name != 'nt'
DEFAULT_VALUES = {
    'config_dir': Path.home() / '.config' / 'dsd' if unix else Path(os.environ['APPDATA']) / 'dsd',
    'elgato_path': None if unix else Path('C:\\Program Files\\Elgato\\StreamDeck\\StreamDeck.exe'),
    'recording_app': 'obs',
    'obs_host': 'localhost',
    'obs_port': 4455,
    'obs_password': None,
    'record_key_combo': 'Alt+Z',
}


class DSDConfig(MutableMapping):
    dsd = None
    obs_host = None
    obs_port = None
    obs_password = None
    elgato_path = Path('C:\\Program Files\\Elgato\\StreamDeck\\StreamDeck.exe')
    recording_app = None
    record_key_combo = None

    def __init__(self, dsd):
        self.dsd = dsd
        self.config_dir = DEFAULT_VALUES['config_dir']
        self.config_path = self.config_dir / 'dsd-config.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.loadout_path = self.config_dir / 'loadouts.json'
                self.config = json.load(f)
                self.config_dir = self.config.get('config_dir', DEFAULT_VALUES['config_dir'])
                self.elgato_path = self.config.get('elgato_path', DEFAULT_VALUES['elgato_path'])
                self.obs_host = self.config.get('obs_host', DEFAULT_VALUES['obs_host'])
                self.obs_port = self.config.get('obs_port', DEFAULT_VALUES['obs_port'])
                self.obs_password = self.config.get('obs_password', DEFAULT_VALUES['obs_password'])
                self.recording_app = self.config.get('recording_app', DEFAULT_VALUES['recording_app'])
                self.record_key_combo = self.config.get('record_key_combo', DEFAULT_VALUES['record_key_combo'])
        else:
            self.config = dict()

    def save(self):
        self.config_dir = Path(self.config_dir)
        self.config_path = self.config_dir / 'dsd-config.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)

        for key, default_value in DEFAULT_VALUES.items():
            value = getattr(self, key)
            if isinstance(value, str) and len(value) == 0:
                value = None

            if value == default_value:
                self.config.pop(key, None)
            elif isinstance(value, Path):
                self.config[key] = str(value)
            else:
                self.config[key] = value

        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=4)

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
