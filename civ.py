import economy
from colors import *

class Civ:
    def __init__(self):
        self.color = PICO_RED
        self.is_enemy = True

class PlayerCiv(Civ):
    def __init__(self):
        Civ.__init__(self)
        self.resources = economy.Resources()
        self.upgrade_limits = economy.Resources()
        self.color = PICO_GREEN
        self.is_enemy = False