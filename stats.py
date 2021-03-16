from collections import defaultdict

VALID_STAT_NAMES = [
    'atomic_bomb',
    'deep_space_drive',
    'fighter_blast_radius',
    'fighter_health_add',
    'fighter_health_mul',
    'fighter_production_halving',
    'fighter_production',
    'fighter_damage_mul',
    'grey_goo',
    'grey_goo_collection',
    'nuclear_instability',
    'overclock',
    'planet_health_aura',
    'planet_health_mul',
    'planet_thorns',
    'pop_growth_min_reduction',
    'pop_max_add',
    'pop_max_mul',
    'reactive_field',
    'ship_death_heal',
    'ship_dodge',
    'ship_fire_rate',
    'ship_health_add',
    'ship_health_mul',
    'ship_missile_speed',
    'ship_regenerate',
    'ship_take_damage_on_fire',
    'ship_weapon_damage',
    'ship_weapon_damage_speed',
    'ship_weapon_range',
    'ship_production_rate',
    'staged_booster_time',
    'top_mining_per_building',
    'top_mining_rate',
    'mining_rate',
    'unstable_reaction',
    'warp_drive',
]

class Stats:
    def __init__(self, **initial):
        self._data = {s:0 for s in VALID_STAT_NAMES}
        for k,v in initial.items():
            if k not in VALID_STAT_NAMES:
                raise Exception("Invalid stat name %s" % k)
            self._data[k] = v

    def __getitem__(self, key):
        return self._data[key]

    def __setitem__(self, key, value):
        self._data[key] = value

    def __add__(self, other):
        if not isinstance(other, Stats):
            raise Exception("Trying to add Stats to non-Stats")

        out = Stats()
        for key in VALID_STAT_NAMES:
            out[key] = self[key] + other[key]

        return out