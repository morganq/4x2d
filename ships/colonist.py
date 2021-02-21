from colors import PICO_BLUE, PICO_DARKBLUE, PICO_WHITE
from particle import Particle
from .ship import Ship, THRUST_PARTICLE_RATE
import random
from v2 import V2

class Colonist(Ship):
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ, "assets/colonist.png")
        self.collision_radius = 4
        self.orbits = True
        self.population = 0

    def can_land(self, other):
        return other == self.target and (other.owning_civ == None or other.owning_civ == self.owning_civ or other.health == 0)

    def collide(self, other):
        if self.can_land(other):
            self.kill()
            if other.owning_civ != self.owning_civ:
                other.change_owner(self.owning_civ)
            other.population += self.population

    def update(self, dt):
        if self.can_land(self.target):
            self.orbits = False
        else:
            self.orbits = True
        return super().update(dt)
