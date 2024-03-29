import math
import random
from collections import defaultdict

import pygame

import aliens
import economy
import funnotification
import sound
from colors import *
from helper import clamp
from icontext import IconText
from intel.inteldata import IntelManager
from optimize import frame_memoize
from stats import Stats
from upgrade import upgrades

V2 = pygame.math.Vector2


class Civ:
    name = None
    def __init__(self, scene):
        self.scene = scene
        self.color = PICO_WHITE
        self.name = ""
        self.is_enemy = True     
        self.is_player = False   
        self.resources = economy.Resources()
        self.frozen = economy.Resources(0,0,0)
        self.num_resource_upgrades = economy.Resources(0,0,0)
        self.base_upgrade_limits = economy.Resources(25,80,150)
        self.upgrade_limits = economy.Resources(9999,9999,9999)
        self.upgrades_stocked = []
        self.upgrades = []
        self.researched_upgrade_names = set()
        self.researched_upgrades_list = []
        self.base_stats = Stats()
        self.frame_stats = {}
        self.total_mined = 0

        self.bonus_supply = 2

        self.offered_upgrades = {}

        self.scarcity = False

        self.upkeep_enabled = True
        self.upkeep_timer = 0

        self.homeworld = None

        self.total_population = 0

        # Analytics
        self.num_upgrades = 0
        self.collection_rate_history = []
        self.collected_this_cycle = 0
        self.collection_cycle_time = 0
        self.time = 0
        self.upgrade_times = []

        # Score
        self.ships_lost = 0
        
        ### Upgrades Stuff ###
        self.nuclear_instability_timer = 0
        self.housing_colonized = False # Turns True when we colonize something
        self.oxygen_cost_per_order = 0
        self.ships_dropping_mines = 0

        self.blueprints = []
        self.comm_objects = []

        ### Modifiers ###
        self.worker_loss = 0
        self.challenge_max_fuel = None
        self.army_max = None
        self.voids = []
        self.planet_void = {}
        self.void_expand_timer = 60
        self.void_color = self.color
        self.max_buildings = 8

    def register_research(self, name):
        self.researched_upgrade_names.add(name)
        self.researched_upgrades_list.append(name)

    def get_fleet_hard_cap(self):
        ups = [upgrades.UPGRADE_CLASSES[n] for n in self.researched_upgrades_list]
        upgrades_max_pop = len([u for u in ups if u.category != 'ships']) + self.bonus_supply
        if self.army_max:
            return min(self.army_max, upgrades_max_pop)
        else:
            return upgrades_max_pop

    def is_fleet_maxed(self):
        return len(self.get_all_combat_ships()) >= self.get_fleet_hard_cap()

    def get_fleet_soft_cap(self):
        return 3

    def update_total_population(self):
        pop = 0
        for planet in self.scene.get_civ_planets(self):
            pop += planet._population
        for colonist in [c for c in self.get_all_ships() if c['name'] == 'colonist']:
            if 'pop' in colonist:
                pop += colonist['pop']
            if colonist['type'] == 'ship':
                pop += colonist['object'].population
        self.total_population = pop

    def get_total_population(self):
        return self.total_population

    def get_fleet_o2_upkeep(self, num_ships = None):
        if num_ships is None:
            num_ships = len(self.get_all_combat_ships())
        if num_ships >= self.get_fleet_soft_cap() + 4:
            return 1
        elif num_ships >= self.get_fleet_soft_cap() + 2:
            return 0.5            
        elif num_ships >= self.get_fleet_soft_cap():
            return 0.25
        return 0

    def get_ship_fuel(self, ship_name):
        f = 9999
        return f

    def get_upgrade_increase_amts(self):
        res_vals = {
            'iron':(25, 170),
            'ice':(80, 185),
            'gas':(150, 230),
        }
           
        data = {}
        for res,i in self.num_resource_upgrades.data.items():
            start, co = res_vals[res]
            new_val = int(start + i * co / math.sqrt((i + 10) * 1.05) - min(i ** 1.45,150))
            if self.scarcity:
                new_val *= 2
            data[res] = new_val - self.base_upgrade_limits.data[res]
        return data   

    def enable_scarcity(self):
        self.base_upgrade_limits.iron += 200
        self.base_upgrade_limits.ice += 200
        self.base_upgrade_limits.gas += 200
        self.scarcity = True
        self.upkeep_update()

    def update(self, dt):
        self.frame_stats = {}
        self.resources_update(dt)
        self.upgrades_update(dt)
        self.upkeep_update()
        self.modifiers_update(dt)
        self.update_total_population()
        self.time += dt

    def modifiers_update(self, dt):
        if self.get_stat("void"):
            self.void_expand_timer -= dt
            if self.void_expand_timer < 0:
                self.void_expand_timer = 60
                for p in self.planet_void:
                    self.planet_void[p].grow()

            # Create void for planets
            for planet in self.scene.get_civ_planets(self):
                if planet not in self.planet_void:
                    void = aliens.alien3void.Alien3Void(self.scene, planet, planet.get_radius() + 10, self.void_color)
                    self.planet_void[planet] = void
                    self.scene.game_group.add(void)

            # Destroy void for destroyed planets
            for planet in list(self.planet_void.keys()):
                if planet.owning_civ != self:
                    self.planet_void[planet].kill()
                    del self.planet_void[planet]

            self.voids = list(self.planet_void.values())

    def get_comm_circles(self):
        self.comm_objects = [o for o in self.comm_objects if o.is_alive()]
        return [(o.pos, o.comm_radius) for o in self.comm_objects]
    
    def in_comm_circle(self, pos):
        for (comm_pos, comm_radius) in self.get_comm_circles():
            if (pos - comm_pos).length_squared() <= comm_radius ** 2:
                return True
        return False

    def upkeep_update(self):
        upkeep = self.get_upkeep_ratio()
        if not self.upkeep_enabled:
            upkeep = 0
        self.upgrade_limits.iron = self.base_upgrade_limits.iron * (1 + upkeep)
        self.upgrade_limits.ice = self.base_upgrade_limits.ice * (1 + upkeep)
        self.upgrade_limits.gas = self.base_upgrade_limits.gas * (1 + upkeep)

    def get_upkeep_ratio(self):
        return 0 # clamp(len(self.get_all_combat_ships()) - 6, 0, 15) * 0.15

    def get_all_ships(self):
        all_ships = []
        for s in self.scene.get_civ_ships(self, skip_objgrid=True):
            if s.is_alive():
                all_ships.append({'type':'ship', 'object':s, 'name':s.SHIP_NAME})
        
        for p in self.scene.get_civ_planets(self, skip_objgrid=True):
            for k,v in p.ships.items():
                for i in range(v):
                    all_ships.append({'type':'planet', 'object':p, 'name':k})
            for (ship_type, data) in p.emit_ships_queue:
                o = {'type':'planet', 'object':p, 'name':ship_type}
                if 'num' in data:
                    o['pop'] = data['num']
                all_ships.append(o)
        return all_ships        

    def get_all_combat_ships(self):
        all_ships = self.get_all_ships()
        return [s for s in all_ships if s['name'].lower() != 'colonist']

    def get_all_fighters(self):
        return [s for s in self.get_all_combat_ships() if s['name'] == "fighter"]

    def resources_update(self, dt):
        for res_type in self.resources.data.keys():
            while self.resources.data[res_type] >= self.upgrade_limits.data[res_type]:
                self.upgrades_stocked.append(res_type)
                self.resources.set_resource(res_type, self.resources.data[res_type] - self.upgrade_limits.data[res_type])
                self.num_resource_upgrades.data[res_type] += 1
                self.base_upgrade_limits.data[res_type] = int(self.base_upgrade_limits.data[res_type] + self.get_upgrade_increase_amts()[res_type])
                self.upkeep_update()
                self.num_upgrades += 1
                self.on_resource_overflow(res_type)

            # frozen
            self.frozen.data[res_type] = max(self.frozen.data[res_type] - dt,0)

        if not self.is_enemy:
            self.collection_cycle_time += dt
            if self.collection_cycle_time > 15:
                self.collection_cycle_time -= 15
                self.collection_rate_history.append(self.collected_this_cycle)
                self.collected_this_cycle = 0
                #print(self.collection_rate_history)

    def on_resource_overflow(self, res_type):
        if not self.is_enemy:
            self.scene.add_asset_button(res_type)
            self.scene.meters[res_type].flash()
            sound.play("upgrade")
            if res_type == 'iron':
                self.upgrade_times.append(self.time)        

            # Award "upgrades" intel after we've gotten at least one of each upgrade
            if (
                self.base_upgrade_limits.iron > 25 and
                self.base_upgrade_limits.ice > 80 and
                self.base_upgrade_limits.gas > 150
            ):
                IntelManager.inst.give_intel("upgrades")

            if self.base_upgrade_limits.iron > 450:
                IntelManager.inst.give_intel("iron")
            if self.base_upgrade_limits.ice > 350:
                IntelManager.inst.give_intel("ice")                
            if self.base_upgrade_limits.gas > 450:
                IntelManager.inst.give_intel("gas")

    def earn_resource(self, resource, value, where = None):
        self.total_mined += value
        if self.frozen.data[resource] <= 0:
            self.resources.set_resource(resource, self.resources.data[resource] + value)
        if not self.is_enemy:
            if resource == "iron":
                self.collected_this_cycle += value / self.upgrade_limits.iron

    def upgrades_update(self, dt):
        if self.get_stat("nuclear_instability"):
            self.nuclear_instability_timer += dt * self.get_stat("nuclear_instability")
            NIT = 60
            if self.nuclear_instability_timer >= NIT:
                self.nuclear_instability_timer = (self.nuclear_instability_timer - NIT) % NIT
                all_fighters = self.get_all_fighters()
                if all_fighters:
                    f = random.choice(all_fighters)
                    if f['type'] == 'ship': f['object'].kill()
                    elif f['type'] == 'planet': 
                        f['object'].ships['fighter'] -= 1
                        f['object'].needs_panel_update = True

    def get_voids(self):
        return self.voids

    def get_stat(self, stat):
        if stat in self.frame_stats:
            return self.frame_stats[stat]
        else:
            value = sum([u.stats[stat] for u in self.upgrades]) + self.base_stats[stat]
            self.frame_stats[stat] = value
            return value

    def can_research(self, uname):
        u = upgrades.UPGRADE_CLASSES[uname]
        if u.name in self.researched_upgrade_names and not u.infinite: return False
        return self.prereqs_met(uname)

    def prereqs_met(self, uname):
        u = upgrades.UPGRADE_CLASSES[uname]
        if not u.requires: return True
        if isinstance(u.requires, str):
            return u.requires in self.researched_upgrade_names
        if isinstance(u.requires, tuple):
            return all([ru in self.researched_upgrade_names for ru in u.requires])
        else:
            return u.requires(self.researched_upgrade_names)

    def offer_upgrades(self, resource, extra_check=None):
        extra_check = extra_check or (lambda u:True)
        if not self.offered_upgrades:
            for upgrade_type, ups in upgrades.UPGRADES[resource].items():
                allowed_ups = [
                    u for u in ups
                    if self.can_research(u) and
                    upgrades.UPGRADE_CLASSES[u].alien == self.is_enemy and
                    extra_check(upgrades.UPGRADE_CLASSES[u])
                ]
                if allowed_ups:
                    uname = random.choice(allowed_ups)
                else:
                    uname = None
                self.offered_upgrades[upgrade_type] = uname
        return self.offered_upgrades

    def clear_offers(self):
        self.offered_upgrades = {}

class PlayerCiv(Civ):
    name = "player"
    def __init__(self, scene):
        Civ.__init__(self, scene)
        self.color = PICO_GREEN
        self.is_player = True
        self.is_enemy = False
        self.void_color = PICO_DARKGREEN

    def get_ship_fuel(self, ship_name):
        f = 9999
        if ship_name == "fighter":
            f = 250
        if self.challenge_max_fuel:
            f = min(f, self.challenge_max_fuel)
            if ship_name == "fighter":
                f = 250 * 0.65
        return f        

    def earn_resource(self, resource, value, where=None):
        if where and value > 0:
            if isinstance(where, V2):
                pos = where
            else:
                pos = where.pos + V2(0, -where.get_radius() - 5)
            it = IconText(pos, None, "+%d" % value, economy.RESOURCE_COLORS[resource])
            xo = 0
            if resource == 'iron': xo = -10
            if resource == 'ice': xo = 0
            if resource == 'gas': xo = 10
            it.pos = pos - V2(it.width, it.height) * 0.5 + V2(xo, 0)
            self.scene.ui_group.add(it)
        return super().earn_resource(resource, value)


class MultiplayerCiv(PlayerCiv):
    def __init__(self, scene, pos):
        super().__init__(scene)
        self.pos = pos

    def on_resource_overflow(self, res_type):
        self.scene.meters[self][res_type].flash()
        self.scene.show_player_upgrade_button(self, res_type)

