from collections import defaultdict

VALID_STAT_NAMES = [
    'asteroid_yield_mul', #test
    'atomic_bomb',
    'battleship_damage_mul',
    'battleship_health_mul', #impl
    'battleship_laser', # impl
    'battleship_production', 
    'bomber_damage_mul',
    'bomber_production', 
    'bomber_raze_chance', #impl
    'colonize_random_building', #impl
    'damage_iron', #test
    'damage_based_on_speed_bonus', #impl , ships deal more damage based on bonus speed
    'deep_space_drive',
    'deserted_regen', #test
    'enclosure_shield', #impl, fleet of size 8 or more gains shield 
    'fighter_blast_radius',
    'fighter_damage_mul',
    'fighter_fire_rate',
    'fighter_health_add',
    'fighter_health_mul',
    'fighter_production_amt_halving',
    'fighter_production',
    'fighter_production_amt',
    'fire_rate_over_time', #impl
    'gas_mining_rate', #impl
    'grey_goo_collection',
    'grey_goo',
    'ice_mining_rate', #impl
    'interceptor_blast_radius',
    'interceptor_missile_bounce',
    'interceptor_production', 
    'interceptor_fire_rate_deep_space', 
    'interceptor_fire_rate_near_bombers', #impl
    'interceptor_damage_mul',
    'interplanetary_missiles', #impl
    'launchpad_pop_chance', #test. chance for +1 pop when sending colonist
    'launchpad_fighter_chance', #test. chance for +1 fighter w bomber/interceptor
    'launchpad_battleship_health', #test. +hp when launching battleship
    'launchpad_battleship_pop', #test. +1 pop when launching battleship
    'mining_rate',
    'mining_rate_at_max_pop', #test
    'mining_rate_proximity', #impl
    'mining_ice_per_iron', #test
    'mining_gas_per_iron', #test
    'nuclear_instability', #lose a ship randomly
    'overclock',
    'planet_health_aura',
    'planet_health_mul',
    'planet_health_per_construct', #impl
    'planet_proximity_health_mul',
    'planet_regen_without_ships', #impl
    'planet_slow_aura', #impl
    'planet_temp_health_mul', 
    'planet_thorns', #impl
    'planet_weapon_boost_zero_pop', # impl
    'pop_growth_min_reduction',
    'pop_growth_rate',
    'pop_growth_rate_per_docked_ship', # impl
    'pop_max_add',
    'pop_max_mul',
    'reactive_field',
    'regen', #test    
    'scarcest_mining_rate',
    'ship_armor_far_from_home', #test
    'ship_shield_far_from_home', #test
    'ship_death_heal',
    'ship_dodge_near_enemy_planets', #test
    'ship_dodge',
    'ship_fire_rate',
    'ship_fire_rate_after_takeoff', #impl
    'ship_health_add',
    'ship_health_mul',
    'ship_missile_speed',
    'ship_production',
    'ship_production_proximity', #impl
    'ship_regenerate',
    'ship_speed_mul_targeting_planets', #test
    'ship_speed_mul', # impl
    'ship_take_damage_on_fire',
    'ship_weapon_damage_speed',
    'ship_weapon_damage',
    'ship_weapon_range',
    'staged_booster_time',
    'stun_nearby_ships', #impl
    'surface_space_missiles', #impl
    'top_mining_per_building',
    'top_mining_rate',
    'underground', # impl, planet buildings don't die when planet is lost
    'unstable_reaction', # planet mining rate boost but lost when attacked
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