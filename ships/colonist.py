from upgrade.upgrades import UPGRADE_CLASSES
from colors import *
from particle import Particle
from planet import planet
from .ship import STATE_WAITING, Ship, THRUST_PARTICLE_RATE, ATMO_DISTANCE
import random
import helper
from v2 import V2
from text import Text

ATOMIC_BOMB_RANGE = 50

class Colonist(Ship):
    HEALTHBAR_SIZE = (16,2)
    BASE_HEALTH = 35
    
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/colonist.png", 12)
        self.collision_radius = 4
        self.population = 0
    
    def set_pop(self, pop):
        self.population = pop
        self.num_label = Text(str(self.population), "small", self.pos + V2(7, -7), PICO_WHITE,shadow=PICO_BLACK)
        self.scene.ui_group.add(self.num_label)

    def can_land(self, other):
        return (
            other == self.effective_target and
            isinstance(other, planet. Planet) and
            (other.owning_civ == None or other.owning_civ == self.owning_civ or other.health < other.get_max_health() / 4)
        )

    def collide(self, other):
        if self.can_land(other):
            self.kill()
            if other.owning_civ != self.owning_civ:
                other.change_owner(self.owning_civ)
            other.population += self.population

            if self.owning_civ.blueprints:
                for upgrade in self.owning_civ.blueprints:
                    UPGRADE_CLASSES[upgrade]().apply(other)
                self.owning_civ.blueprints = []

            other.needs_panel_update = True


    def update(self, dt):
        super().update(dt)
        self.num_label.pos = self.pos + V2(7, -7)

    def kill(self):
        if self.get_stat("atomic_bomb"):
            print("nuke")
            range_adjust = 0.75 + self.population * 0.25
            enemy_objs = self.scene.get_enemy_objects(self.owning_civ)
            near_enemies = helper.all_nearby(self.pos, enemy_objs, ATOMIC_BOMB_RANGE * range_adjust)
            for enemy in near_enemies:
                enemy.take_damage(50, self)
            # TODO: particles
            
        self.num_label.kill()
        return super().kill()

    def state_cruising(self, dt):
        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, planet.Planet):
            if (delta.magnitude() - self.effective_target.radius - ATMO_DISTANCE) <= 0:
                if not self.can_land(self.effective_target):
                    self.set_state(STATE_WAITING)
                    return        
        return super().state_cruising(dt)