from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from dsdultra.buttons.group import ButtonGroup

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
                    c['icon'] = Path(__file__).resolve().parent.parent / 'assets' / (c['icon'] if c['icon'] else 'icons/groups/blank72.png')
                    c['content_class'] = ButtonGroup
                    categories[c['id']] = c

    # Enumerate children of groups once
    for category in categories.values():
        category['children'] = []
    for category in categories.values():
        parent_id = category.get('parent')
        if parent_id and parent_id in categories:
            categories[parent_id]['children'].append(category['id'])

    return categories


class SuperDestroyer:

    def __init__(self, dsd):
        self.dsd: 'DSDUltra' = dsd
        self.categories = get_categories()
        self.weapons = StratagemGroup(self.categories['weapons'], self.dsd.stratagems)
        self.vehicles = StratagemGroup(self.categories['vehicles'], self.dsd.stratagems)
        self.emplacements = StratagemGroup(self.categories['emplacements'], self.dsd.stratagems)
        self.backpacks = StratagemGroup(self.categories['backpacks'], self.dsd.stratagems)
        self.sentries = StratagemGroup(self.categories['sentries'], self.dsd.stratagems)
        self.mines = StratagemGroup(self.categories['mines'], self.dsd.stratagems)
        self.eagles = StratagemGroup(self.categories['eagles'], self.dsd.stratagems)
        self.orbitals = StratagemGroup(self.categories['orbitals'], self.dsd.stratagems)
        self.mission = StratagemGroup(self.categories['mission'], self.dsd.stratagems)
        self.common = StratagemGroup(self.categories['common'], self.dsd.stratagems)
        self.all = {}
        for group in [self.weapons, self.vehicles, self.emplacements, self.backpacks,
                      self.sentries, self.mines, self.eagles, self.orbitals,
                      self.mission, self.common]:
            self.all.update(group.items)


class StratagemGroup:
    def __init__(self, data, items):
        self.id = data.get('id')
        self.name = data.get('name')
        self.color = data.get('color', 'yellow')
        self.full = data.get('full', False)
        self.icon = Path(__file__).resolve().parent.parent / 'assets' / data.get('icon')
        self.items = {}
        filter_type = data.get('filter_type', None)
        filter_attributes = data.get('filter_attributes', None)
        for i in items.values():
            if filter_type:
                if i.type != filter_type:
                    continue
            if not i.filter(filter_attributes):
                continue
            self.items[i.id] = i

    def __iter__(self):
        return iter(self.items.values())

    def __len__(self):
        return len(self.items)

    def __getitem__(self, key):
        return self.items[key]

    def __contains__(self, item):
        return item in self.items

    def values(self):
        return list(self.items.values())

    def keys(self):
        return self.items.keys()

    def __str__(self):
        return f'<StratagemGroup:{self.id}>'

    def __repr__(self):
        return str(self)