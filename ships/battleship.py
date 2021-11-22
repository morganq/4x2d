import math
import random

import explosion
import planet
import sound
from bullet import Bullet
from colors import *
from helper import all_nearby, clamp
from laserparticle import LaserParticle
from particle import Particle
from v2 import V2

from ships.all_ships import register_ship
from ships.fighter import STATE_DOGFIGHT, Fighter
from ships.ship import (STATE_CRUISING, STATE_WAITING, THRUST_PARTICLE_RATE,
                        Ship)


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

    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self._set_player_ship_sprite_sheet()

    def get_max_health(self):
        mh = super().get_max_health()
        mh *= 1 + self.get_stat("battleship_health_mul")
        if not self.owning_civ.is_enemy:
            hp_curve = [1, 2.0, 2.65, 3.0]
            mh *= hp_curve[self.scene.game.run_info.ship_levels["battleship"] - 1]
        return mh

    def get_fire_rate(self):
        fr = super().get_fire_rate()
        if self.get_stat("battleship_laser"):
            fr *= 2.5
        return fr

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        if self.get_stat("battleship_laser"):
            mods['damage_base'] = 4
        if not self.owning_civ.is_enemy:
            damage_curve = [1, 1.5, 1.9, 2.2]
            mods['damage_base'] *= damage_curve[self.scene.game.run_info.ship_levels["battleship"] - 1]        
        return mods

    def fire_laser(self, at):
        lp = LaserParticle(self.pos, at.pos, PICO_PINK, 0.75)
        self.scene.game_group.add(lp)
        mods = self.prepare_bullet_mods()
        b = Bullet(at.pos, at, self, mods=mods)
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


    def emit_thrust_particles(self):
        def sfn(t):
            if t < 0.125:
                return t * 8
            return 1 - (t - 0.125)
        e = explosion.Explosion(self.pos + -self.velocity, [PICO_WHITE, PICO_YELLOW, PICO_YELLOW, PICO_ORANGE, PICO_RED], 3, 4, sfn, 4)
        self.scene.game_group.add(e)
