import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dsdultra.dsd import DSDUltra


def get_categories():
    categories = {}
    json_dir = Path(__file__).resolve().parent.parent / 'assets' / 'armory'
    custom_dir = json_dir / 'custom'
    category_paths = [json_dir / 'categories.json']
    custom_category_path = custom_dir / 'categories.json'
    if custom_category_path.exists():
        category_paths.append(custom_category_path)
    for path in category_paths:
        for json_file in category_paths:
            with json_file.open(encoding='utf-8') as file:
                data = json.load(file)
                for c in data.values():
                    categories[c['id']] = c
    return categories


class SuperDestroyer:

    def __init__(self, dsd):
        self.dsd: 'DSDUltra' = dsd
        categories = get_categories()
        self.weapons = StratagemGroup(categories['weapons'], self.dsd.stratagems)
        self.vehicles = StratagemGroup(categories['vehicles'], self.dsd.stratagems)
        self.emplacements = StratagemGroup(categories['emplacements'], self.dsd.stratagems)
        self.backpacks = StratagemGroup(categories['backpacks'], self.dsd.stratagems)
        self.sentries = StratagemGroup(categories['sentries'], self.dsd.stratagems)
        self.mines = StratagemGroup(categories['mines'], self.dsd.stratagems)
        self.eagles = StratagemGroup(categories['eagles'], self.dsd.stratagems)
        self.orbitals = StratagemGroup(categories['orbitals'], self.dsd.stratagems)
        self.mission = StratagemGroup(categories['mission'], self.dsd.stratagems)
        self.common = StratagemGroup(categories['common'], self.dsd.stratagems)


class StratagemGroup:
    def __init__(self, data, items):
        self.id = data.get('id')
        self.name = data.get('name')
        self.color = data.get('color', 'yellow')
        self.full = data.get('full', False)
        self.icon = data.get('icon')
        self.items = []
        filter_type = data.get('filter_type', None)
        filter_attributes = data.get('filter_attributes', None)
        for i in items.values():
            if filter_type:
                if i.type != filter_type:
                    continue
            if filter_attributes:
                for attr in filter_attributes:
                    if attr.startswith('!'):
                        if getattr(i, attr[1:], False):
                            continue
                    else:
                        if not getattr(i, attr, False):
                            continue
            self.items.append(i)

    def __iter__(self):
        return iter(self.items)

    def __len__(self):
        return len(self.items)
