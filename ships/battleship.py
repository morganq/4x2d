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
import sound
from laserparticle import LaserParticle
from ships.all_ships import register_ship

@register_ship
class Battleship(Fighter): 
    BASE_HEALTH = 160
    BLAST_RADIUS = 0
    FIRE_RATE = 1.5
    BASE_DAMAGE = 6

    FIRE_RANGE = 40
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = True
    DOGFIGHTS = True

    SHIP_NAME = "battleship"
    SHIP_BONUS_NAME = "battleship"

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/battleship.png", 12)

    def get_max_health(self):
        mh = super().get_max_health()
        mh *= 1 + self.get_stat("battleship_health_mul")
        return mh

    def get_fire_rate(self):
        fr = super().get_fire_rate()
        if self.get_stat("battleship_laser"):
            fr *= 1.25
        return fr

    def fire_laser(self, at):
        lp = LaserParticle(self.pos, at.pos, PICO_PINK, 0.25)
        self.scene.game_group.add(lp)
        b = Bullet(at.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)        
        
        enemies = self.scene.get_enemy_objects(self.owning_civ)
        threat_range = self.THREAT_RANGE_DEFAULT
        if self.chosen_target.owning_civ == self.owning_civ: # Target is our own planet (defense)
            threat_range = self.THREAT_RANGE_DEFENSE
        threats = [
            e for e in enemies
            if ((e.pos - self.pos).sqr_magnitude() < threat_range ** 2 and e.is_alive())
        ]

        sound.play(random.choice(['laser1', 'laser2', 'laser3']))

        if threats:
            self.effective_target = random.choice(threats)

    def fire(self, at):
        if self.get_stat("battleship_laser"):
            self.fire_laser(at)
            return

        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(self.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)               
