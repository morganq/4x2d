from collections import defaultdict

VALID_STAT_NAMES = [
    'alien_control_mul',
    'armory', # TODO: implement
    'asteroid_yield_mul', 
    'atomic_bomb',
    'battleship_damage_mul',
    'battleship_health_mul',
    'battleship_laser',
    'battleship_production', 
    'bomber_colonist', 
    'bomber_damage_mul',
    'bomber_dodge_num',
    'bomber_production', 
    'bomber_raze_chance',
    'colonize_random_building', 
    'damage_iron',
    'decoy', #Enemy fighters that fly nearby will retarget to attack this planet
    'deep_space_drive',
    'deserted_regen', # x
    'enclosure_shield', 
    'fighter_blast_radius',
    'fighter_damage_mul',
    'fighter_damage_iron',
    'fighter_fire_rate',
    'fighter_health_add',
    'fighter_health_mul',
    'fighter_production_amt_halving',
    'fighter_production', # production speed
    'fighter_production_amt',
    'fighter_regen',
    'fire_rate_over_time', 
    'gas_mining_rate',
    'grey_goo_collection',
    'grey_goo',
    'hacking', # modifier
    'headquarters', # +1 pop when worker sent from here colonizes
    'ice_mining_rate',
    'ice_per_docked', # "Every 5 seconds, gain [^+1] Ice for each docked ship"
    'interceptor_blast_radius',
    'interceptor_damage_mul',
    'interceptor_fire_rate_deep_space', 
    'interceptor_fire_rate_near_bombers',    
    'interceptor_missile_bounce',
    'interceptor_production', 
    'interceptor_shield',
    'interplanetary_missiles',
    'launchpad_pop_chance', #chance for +1 pop when sending workers
    'launchpad_fighter_chance', #chance for +1 fighter w bomber/interceptor
    'launchpad_battleship_health', #+hp when launching battleship
    'launchpad_battleship_pop', #+1 pop when launching battleship
    'lost_planet_upgrade',
    'max_pop_growth', # +1 max pop every 30 seconds
    'max_ships_mul',
    'max_ships_per_planet', 
    'memorial', # +1 fighter when ship sent from here dies
    'mining_rate',
    'mining_rate_first_120', 
    'mining_rate_at_max_pop', 
    'mining_rate_proximity', 
    'mining_ice_per_iron',
    'mining_gas_per_iron', 
    'nuclear_instability', #lose a ship randomly
    'overclock',
    'planet_health_aura',
    'planet_health_mul',
    'planet_health_per_construct', 
    'planet_proximity_health_mul',
    'planet_regen_without_ships', 
    'planet_self_destruct', # explodes in 30 seconds
    'planet_shield', 
    'planet_slow_aura', 
    'planet_temp_health_mul', 
    'planet_weapon_boost',
    'planet_weapon_boost_zero_pop',
    'planet_weapon_boost_zero_ships',
    'pop_growth_min_reduction',
    'pop_growth_rate',
    'pop_growth_rate_per_docked_ship',
    'pop_growth_without_ships',
    'pop_max_add',
    'pop_max_mul',
    'prevent_buildings',
    'raze_upgrade', 
    'reactive_field',
    'regen', 
    'scarcest_mining_rate',
    'scout_bombs',
    'scout_damage_mul',
    'scout_production', # production speed
    'scout_stealth', # scouts gain stealth
    'ship_armor_far_from_home', 
    'ship_armor',
    'ship_shield_far_from_home', 
    'ship_death_heal',
    'ship_dodge_near_enemy_planets', 
    'ship_dodge',
    'ship_fire_rate',
    'ship_fire_rate_after_takeoff',
    'ship_health_add',
    'ship_health_mul',
    'ship_missile_speed',
    'ship_pop_boost', # Ships launched from this planet gain [^+10%] speed and [^+5%] attack speed per population
    'ship_production',
    'ship_production_rate_per_pop',
    'ship_production_proximity',
    'ship_regenerate',
    'ship_speed_mul_targeting_planets',
    'ship_speed_mul', # Multiplier on ship speed
    'ship_take_damage_on_fire',
    'ship_weapon_damage_speed',
    'ship_weapon_damage',
    'ship_weapon_range',
    'staged_booster_time',
    'stun_nearby_ships',
    'surface_space_missiles', 
    'terraform', # modifier
    'top_mining_per_building',
    'top_mining_rate',
    'underground', # planet buildings don't die when planet is lost
    'unstable_reaction', # planet mining rate boost but lost when attacked
    'warp_drive',
    'warp_drive_pop_chance', #chance to gain pop when colonist jumps
    'void', # modifier
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
