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
    BASE_HEALTH = 35
    BLAST_RADIUS = 0
    FIRE_RATE = 0.2
    BASE_DAMAGE = 40

    FIRE_RANGE = 40
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = True
    DOGFIGHTS = False

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/bomber.png", 12)

    def fire(self, at):
        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        damage_add = 0
        extra_speed = (self.get_max_speed() - Ship.MAX_SPEED) / Ship.MAX_SPEED
        damage_add += self.get_stat("ship_weapon_damage_speed") * clamp(extra_speed, 0, 1)
        damage_add += self.get_stat("ship_weapon_damage")
        damage_mul = self.get_stat("bomber_damage_mul")
        blast_radius = self.BLAST_RADIUS + self.get_stat("bomber_blast_radius")
        b = Bullet(self.pos, at, self, mods={
            'grey_goo': self.get_stat('grey_goo'),
            'damage_base': self.BASE_DAMAGE,
            'damage_mul': damage_mul,
            'damage_add': damage_add,
            'blast_radius': blast_radius,
            'ship_missile_speed':self.get_stat("ship_missile_speed"),
            'color':PICO_PINK
        })
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)               
