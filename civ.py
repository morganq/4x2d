import economy
from upgrade import upgrades
from colors import *
from collections import defaultdict
import random

class Civ:
    def __init__(self, scene):
        self.scene = scene
        self.color = PICO_RED
        self.is_enemy = True        
        self.resources = economy.Resources()
        self.frozen = economy.Resources(0,0,0)
        self.upgrade_limits = economy.Resources(50,50,50)
        self.upgrades_stocked = []
        self.upgrades = []
        self.researched_upgrade_names = set()

        self.offered_upgrades = {}
        
        ### Upgrades Stuff ###
        self.nuclear_instability_timer = 0

        self.blueprints = []

    def update(self, dt):
        self.resources_update(dt)
        self.upgrades_update(dt)

    def get_all_fighters(self):
        all_fighters = []
        for s in self.scene.get_civ_ships(self):
            if s.SHIP_NAME == 'fighter':
                all_fighters.append({'type':'ship', 'object':s})
        
        for p in self.scene.get_civ_planets(self):
            if p.ships['fighter'] > 0:
                for i in range(p.ships['fighter']):
                    all_fighters.append({'type':'planet', 'object':p})
        return all_fighters

    def resources_update(self, dt):
        for res_type in self.resources.data.keys():
            while self.resources.data[res_type] >= self.upgrade_limits.data[res_type]:
                self.upgrades_stocked.append(res_type)
                self.resources.set_resource(res_type, self.resources.data[res_type] - self.upgrade_limits.data[res_type])
                self.upgrade_limits.data[res_type] += 25

            # frozen
            self.frozen.data[res_type] = max(self.frozen.data[res_type] - dt,0)

    def earn_resource(self, resource, value):
        if self.frozen.data[resource] <= 0:
            self.resources.set_resource(resource, self.resources.data[resource] + value)

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
        return sum([u.stats[stat] for u in self.upgrades])

    def can_research(self, uname):
        u = upgrades.UPGRADE_CLASSES[uname]
        if u.name in self.researched_upgrade_names and not u.infinite: return False
        return self.prereqs_met(uname)

    def prereqs_met(self, uname):
        u = upgrades.UPGRADE_CLASSES[uname]
        if not u.requires: return True
        if isinstance(u.requires, tuple):
            return all([ru in self.researched_upgrade_names for ru in u.requires])
        else:
            return u.requires(self.researched_upgrade_names)

    def offer_upgrades(self, resource):

        if not self.offered_upgrades:
            for upgrade_type, ups in upgrades.UPGRADES[resource].items():
                allowed_ups = [
                    u for u in ups
                    if self.can_research(u) and
                    upgrades.UPGRADE_CLASSES[u].alien == self.is_enemy
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
    def __init__(self, scene):
        Civ.__init__(self, scene)
        self.color = PICO_GREEN
        self.is_enemy = False