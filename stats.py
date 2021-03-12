from collections import defaultdict

VALID_STAT_NAMES = [
    'fire_rate',
    'ship_health',
    'warp_drive',
    'top_mining_rate',
    'top_mining_per_building',
    'pop_max_mul',
    'pop_max_add',
    'fighter_production',
    'fighter_production_halving',
    'planet_health_mul',
    'planet_health_aura',
    'planet_thorns'
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