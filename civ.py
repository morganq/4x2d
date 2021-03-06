import economy
from colors import *
from collections import defaultdict

class Civ:
    def __init__(self):
        self.color = PICO_RED
        self.is_enemy = True        
        self.resources = economy.Resources()
        self.upgrade_limits = economy.Resources(50,50,50)
        self.upgrades_stocked = []
        self.upgrades = []

    def get_stat(self, stat):
        return sum([u[stat] for u in self.upgrades])

class PlayerCiv(Civ):
    def __init__(self):
        Civ.__init__(self)
        self.color = PICO_GREEN
        self.is_enemy = False