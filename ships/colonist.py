from colors import *
from particle import Particle
from .ship import Ship, THRUST_PARTICLE_RATE
import random
from v2 import V2
from text import Text

class Colonist(Ship):
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ, "assets/colonist.png")
        self.collision_radius = 4
        self.orbits = True
        self.population = 0
    
    def set_pop(self, pop):
        self.population = pop
        self.num_label = Text(str(self.population), "small", self.pos + V2(7, -7), PICO_WHITE,shadow=PICO_BLACK)
        self.scene.ui_group.add(self.num_label)

    def can_land(self, other):
        return other == self.target and (other.owning_civ == None or other.owning_civ == self.owning_civ or other.health < other.get_max_health() / 4)

    def collide(self, other):
        if self.can_land(other):
            self.kill()
            if other.owning_civ != self.owning_civ:
                other.change_owner(self.owning_civ)
            other.population += self.population
            other.needs_panel_update = True

    def update(self, dt):
        if self.can_land(self.target):
            self.orbits = False
        else:
            self.orbits = True
        self.default_update(dt)
        self.num_label.pos = self.pos + V2(7, -7)
        return super().update(dt)

    def kill(self):
        self.num_label.kill()
        return super().kill()