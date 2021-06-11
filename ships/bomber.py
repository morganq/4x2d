from ships.fighter import Fighter, STATE_DOGFIGHT
from ships.ship import Ship, THRUST_PARTICLE_RATE, STATE_WAITING, STATE_CRUISING
from colors import *
from particle import Particle
from v2 import V2
import random
import math
import planet
from helper import all_nearby, clamp
from bullet import Bullet

class Bomber(Fighter): 
    SHIP_NAME = "bomber"
    SHIP_BONUS_NAME = "bomber"
    BASE_HEALTH = 55
    BLAST_RADIUS = 0
    FIRE_RATE = 0.4
    BASE_DAMAGE = 30

    FIRE_RANGE = 35
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = True
    DOGFIGHTS = False

    # TODO: waiting-style movement for siege

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/bomber.png", 12)

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
