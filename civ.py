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
        self.upgrade_limits = economy.Resources(50,50,50)
        self.upgrades_stocked = []
        self.upgrades = []
        self.researched_upgrade_names = set()

        ### Upgrades Stuff ###
        self.nuclear_instability_timer = 0

    def update(self, dt):
        self.upgrades_update(dt)

    def upgrades_update(self, dt):
        if self.get_stat("nuclear_instability"):
            self.nuclear_instability_timer += dt * self.get_stat("nuclear_instability")
            NIT = 60
            if self.nuclear_instability_timer >= NIT:
                self.nuclear_instability_timer = (self.nuclear_instability_timer - NIT) % NIT
                ships = self.scene.get_civ_ships(self)
                if ships:
                    random.choice(ships).kill()
                    # TODO: particles


    def get_stat(self, stat):
        return sum([u.stats[stat] for u in self.upgrades])

class PlayerCiv(Civ):
    def __init__(self, scene):
        Civ.__init__(self, scene)
        self.color = PICO_GREEN
        self.is_enemy = False

        self.offered_upgrades = {}

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
                allowed_ups = [u for u in ups if self.can_research(u)]
                uname = random.choice(allowed_ups)
                self.offered_upgrades[upgrade_type] = uname
        return self.offered_upgrades

    def clear_offers(self):
        self.offered_upgrades = {}