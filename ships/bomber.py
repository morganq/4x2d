import math
import random

import particle
import planet
from bullet import Bullet
from colors import *
from helper import all_nearby, clamp
from particle import Particle
import pygame
V2 = pygame.math.Vector2

import ships
from ships.all_ships import register_ship
from ships.fighter import STATE_DOGFIGHT, Fighter
from ships.ship import (STATE_CRUISING, STATE_WAITING, THRUST_PARTICLE_RATE,
                        Ship)


@register_ship
class Bomber(Fighter): 
    SHIP_NAME = "bomber"
    SHIP_BONUS_NAME = "bomber"
    BASE_HEALTH = 45
    BLAST_RADIUS = 0
    FIRE_RATE = 0.4
    BASE_DAMAGE = 25

    FIRE_RANGE = 35
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = True
    DOGFIGHTS = False

    FUEL = 9999

    # TODO: waiting-style movement for siege

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self._set_player_ship_sprite_sheet()
        self.can_create_colonist = True
        self.num_dodges = 0
        self.last_shot_at = None

    def get_dodges_left(self):
        return self.get_stat("bomber_dodge_num") - self.num_dodges

    def dodge(self):
        self.num_dodges += 1

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        if not self.owning_civ.is_enemy:
            damage_curve = [1, 1.5, 1.9, 2.2]
            mods['damage_base'] *= damage_curve[self.scene.game.run_info.ship_levels["bomber"] - 1]
        mods['raze_chance'] = self.get_stat("bomber_raze_chance")
        mods['color'] = PICO_RED
        mods['shape'] = 'circle'
        mods['size'] = 1
        mods['missile_speed'] = -0.3
        mods['trail'] = PICO_RED
        return mods

    def fire(self, at):
        towards = (at.pos - self.pos).normalize()
        self.last_shot_at = at

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(self.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalize() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)             

    def update(self, dt):
        if (
            isinstance(self.chosen_target, planet.planet.Planet) and
            self.chosen_target.health <= 0 and
            self.chosen_target == self.last_shot_at and
            self.can_create_colonist and
            self.get_stat("bomber_colonist")
        ):
            s = ships.colonist.Colonist(self.scene, self.pos, self.owning_civ)
            s.set_pop(1)
            s.set_target(self.chosen_target)
            self.scene.game_group.add(s)
            self.can_create_colonist = False
        return super().update(dt)

    def get_max_health(self):
        hp = super().get_max_health()
        if not self.owning_civ.is_enemy:
            hp_curve = [1, 1.6, 2.1, 2.6]
            hp *= hp_curve[self.scene.game.run_info.ship_levels["bomber"] - 1]           
        return hp

    def emit_thrust_particles(self):
        pvel = V2(random.random() - 0.5, random.random() - 0.5) * 1
        pvel += -self.velocity / 2
        vn = self.velocity.normalize()
        side = V2(vn.y, -vn.x) # Sideways vector from forward
        p1 = particle.Particle([PICO_WHITE, PICO_RED, PICO_RED], 1, self.pos + -self.velocity.normalize() * self.radius + side * 2, 0.75, pvel)
        self.scene.add_particle(p1)
        p2 = particle.Particle([PICO_WHITE, PICO_RED, PICO_RED], 1, self.pos + -self.velocity.normalize() * self.radius - side * 2, 0.75, pvel)
        self.scene.add_particle(p2)
        p3 = particle.Particle([PICO_WHITE, PICO_RED, PICO_RED], 1, self.pos + -self.velocity.normalize() * self.radius, 1.5, pvel)
        self.scene.add_particle(p3)
