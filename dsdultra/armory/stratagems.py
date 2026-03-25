import json
from pathlib import Path


class Stratagem:
    id: str
    name: str
    short_name: str
    icon: str
    cooldown: int
    max_cooldown: int | None
    use_cooldown: int | None
    max_use_cooldown: int | None
    summon_time: float
    max_summon_time: float | None
    code: list[str]
    passengers: int | None
    annotation: str | None
    type: str | None
    is_arc: bool
    is_backpack: bool
    is_barrage: bool
    is_disposable: bool
    is_energy: bool
    is_explosive: bool
    is_fire: bool
    is_gas: bool
    is_laser: bool
    is_melee: bool
    is_mortar: bool
    is_plasma: bool
    is_shield: bool
    is_stun: bool
    is_tower: bool
    is_vehicle: bool

    def __init__(self, data):
        self.id = data.get('id')
        self.name = data.get('name')
        self.short_name = data.get('short_name')
        self.icon = data.get('icon')
        self.cooldown = data.get('cooldown', 0)
        self.max_cooldown = data.get('max_cooldown', None)
        self.use_cooldown = data.get('use_cooldown', None)
        self.max_use_cooldown = data.get('max_use_cooldown', None)
        self.summon_time = data.get('summon_time', 0)
        self.max_summon_time = data.get('max_summon_time', None)
        self.code = data.get('code', [])
        self.passengers = data.get('passengers', None)
        self.annotation = data.get('annotation', None)
        self.type = data.get('type', None)
        self.is_arc = data.get('is_arc', False)
        self.is_backpack = data.get('is_backpack', False)
        self.is_barrage = data.get('is_barrage', False)
        self.is_disposable = data.get('is_disposable', False)
        self.is_energy = data.get('is_energy', False)
        self.is_explosive = data.get('is_explosive', False)
        self.is_fire = data.get('is_fire', False)
        self.is_gas = data.get('is_gas', False)
        self.is_laser = data.get('is_laser', False)
        self.is_melee = data.get('is_melee', False)
        self.is_mortar = data.get('is_mortar', False)
        self.is_plasma = data.get('is_plasma', False)
        self.is_shield = data.get('is_shield', False)
        self.is_stun = data.get('is_stun', False)
        self.is_tower = data.get('is_tower', False)
        self.is_vehicle = data.get('is_vehicle', False)

        for direction in self.code:
            if direction not in {'up', 'down', 'left', 'right'}:
                raise ValueError(f"Invalid direction '{direction}' in stratagem code for '{self.name}'. Only 'up', 'down', 'left', or 'right' are allowed.")

    @staticmethod
    def load_stratagems():
        stratagems = {}
        json_dir = Path(__file__).resolve().parent.parent / 'assets' / 'armory'
        custom_dir = json_dir / 'custom'
        armory_dirs = [
            json_dir / 'requisitions',
            json_dir / 'warbonds',
        ]
        if custom_dir.exists():
            armory_dirs.append(custom_dir)
        custom_categories_file = custom_dir / 'categories.json'

        for armory_dir in armory_dirs:
            for json_file in sorted(armory_dir.glob('*.json')):
                if json_file == custom_categories_file:
                    continue
                with json_file.open(encoding='utf-8') as file:
                    data = json.load(file)
                for stratagem_data in data.values():
                    item = Stratagem(stratagem_data)
                    stratagems[item.id] = item
        return stratagems