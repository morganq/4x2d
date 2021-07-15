import math
import random

import planet
from bullet import Bullet
from colors import *
from helper import all_nearby, clamp
from particle import Particle
from v2 import V2

import ships
from ships.all_ships import register_ship
from ships.fighter import STATE_DOGFIGHT, Fighter
from ships.ship import (STATE_CRUISING, STATE_WAITING, THRUST_PARTICLE_RATE,
                        Ship)


@register_ship
class Bomber(Fighter): 
    SHIP_NAME = "bomber"
    SHIP_BONUS_NAME = "bomber"
    BASE_HEALTH = 55
    BLAST_RADIUS = 0
    FIRE_RATE = 0.4
    BASE_DAMAGE = 40

    FIRE_RANGE = 35
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = True
    DOGFIGHTS = False

    # TODO: waiting-style movement for siege

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/bomber.png", 12)
        self.can_create_colonist = False

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['raze_chance'] = self.get_stat("bomber_raze_chance")
        mods['raze_make_colonist'] = self.get_stat('bomber_colonist')
        mods['color'] = PICO_PINK
        return mods

    def fire(self, at):
        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(self.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)    

    def set_target(self, target):
        if target.owning_civ and target.owning_civ != self.owning_civ:
            self.can_create_colonist = True
        return super().set_target(target)           

    def update(self, dt):
        if (
            isinstance(self.effective_target, planet.planet.Planet) and
            self.effective_target.health <= 0 and
            self.can_create_colonist and
            self.get_stat("bomber_colonist")
        ):
            s = ships.colonist.Colonist(self.scene, self.pos, self.owning_civ)
            s.set_pop(1)
            s.set_target(self.effective_target)
            self.shooter.scene.game_group.add(s)
            self.can_create_colonist = False
        return super().update(dt)
