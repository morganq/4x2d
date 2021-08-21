import random
from collections import defaultdict

import economy
import sound
from colors import *
from helper import clamp
from icontext import IconText
from optimize import frame_memoize
from stats import Stats
from upgrade import upgrades
from v2 import V2


class Civ:
    name = None
    def __init__(self, scene):
        self.scene = scene
        self.color = PICO_RED
        self.is_enemy = True        
        self.resources = economy.Resources()
        self.frozen = economy.Resources(0,0,0)
        self.base_upgrade_limits = economy.Resources(25,80,150)
        self.upgrade_limits = economy.Resources(9999,9999,9999)
        self.upgrades_stocked = []
        self.upgrades = []
        self.researched_upgrade_names = set()
        self.base_stats = Stats()
        self.frame_stats = {}

        self.offered_upgrades = {}

        self.scarcity = False

        self.upkeep_enabled = True
        self.upkeep_timer = 0

        # Analytics
        self.num_upgrades = 0
        self.collection_rate_history = []
        self.collected_this_cycle = 0
        self.collection_cycle_time = 0
        self.time = 0
        self.upgrade_times = []
        
        ### Upgrades Stuff ###
        self.nuclear_instability_timer = 0
        self.housing_colonized = False # Turns True when we colonize something

        self.blueprints = []

    def get_upgrade_increase_amts(self):
        if self.scarcity:
            return {
                'iron':30 * 4,
                'ice':35 * 4,
                'gas':50 * 4
            }            
        else:
            return {
                'iron':30,
                'ice':35,
                'gas':50
            }        

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
        self.time += dt

    def upkeep_update(self):
        upkeep = self.get_upkeep_ratio()
        if not self.upkeep_enabled:
            upkeep = 0
        self.upgrade_limits.iron = self.base_upgrade_limits.iron * (1 + upkeep)
        self.upgrade_limits.ice = self.base_upgrade_limits.ice
        self.upgrade_limits.gas = self.base_upgrade_limits.gas

    def get_upkeep_ratio(self):
        return clamp(len(self.get_all_combat_ships()) - 6, 0, 15) * 0.075

    def get_all_combat_ships(self):
        all_ships = []
        for s in self.scene.get_civ_ships(self, skip_objgrid=True):
            if s.SHIP_BONUS_NAME != 'colonist' and s.is_alive():
                all_ships.append({'type':'ship', 'object':s, 'name':s.SHIP_NAME})
        
        for p in self.scene.get_civ_planets(self, skip_objgrid=True):
            for k,v in p.ships.items():
                for i in range(v):
                    all_ships.append({'type':'planet', 'object':p, 'name':k})
            for (ship_type, data) in p.emit_ships_queue:
                all_ships.append({'type':'planet', 'object':p, 'name':ship_type})

        return all_ships

    def get_all_fighters(self):
        return [s for s in self.get_all_combat_ships() if s['name'] == "fighter"]

    def resources_update(self, dt):
        for res_type in self.resources.data.keys():
            while self.resources.data[res_type] >= self.upgrade_limits.data[res_type]:
                self.upgrades_stocked.append(res_type)
                self.resources.set_resource(res_type, self.resources.data[res_type] - self.upgrade_limits.data[res_type])
                self.base_upgrade_limits.data[res_type] = int(self.base_upgrade_limits.data[res_type] + self.get_upgrade_increase_amts()[res_type])
                self.upkeep_update()
                self.num_upgrades += 1
                if not self.is_enemy:
                    self.scene.add_asset_button(res_type)
                    self.scene.meters[res_type].flash()
                    sound.play("upgrade")
                    if res_type == 'iron':
                        self.upgrade_times.append(self.time)

            # frozen
            self.frozen.data[res_type] = max(self.frozen.data[res_type] - dt,0)

        if not self.is_enemy:
            self.collection_cycle_time += dt
            if self.collection_cycle_time > 15:
                self.collection_cycle_time -= 15
                self.collection_rate_history.append(self.collected_this_cycle)
                self.collected_this_cycle = 0
                #print(self.collection_rate_history)

    def earn_resource(self, resource, value, where = None):
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
        self.is_enemy = False

    def earn_resource(self, resource, value, where=None):
        if where and value > 0:
            if isinstance(where, V2):
                pos = where
            else:
                pos = where.pos + V2(0, -where.get_radius() - 5)
            self.scene.score += value
            it = IconText(pos, None, "+%d" % value, economy.RESOURCE_COLORS[resource])
            it.pos = pos - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
            self.scene.ui_group.add(it)
        return super().earn_resource(resource, value)
