import os
import json
from pathlib import Path
from collections.abc import MutableMapping

class DSDConfig(MutableMapping):
    config_path = Path(os.getcwd()) / 'dsd-config.json'

    def __init__(self, dsd):
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
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