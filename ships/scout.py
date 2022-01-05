import random

import bullet
import meter
import particle
import pygame
from colors import *
from planet import planet
from simplesprite import SimpleSprite
from v2 import V2

from ships import fighter
from ships.all_ships import register_ship


@register_ship
class Scout(fighter.Fighter):
    SHIP_NAME = "scout"
    SHIP_BONUS_NAME = "scout"
    BASE_HEALTH = 15
    BASE_DAMAGE = 3
    FIRE_RATE = 0.5
    FIRE_RANGE = 36
    DOGFIGHTS = True
    BOMBS = True
    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self._set_player_ship_sprite_sheet()
        self.busters = 2
        self.max_busters = 2
        self.buster_time = 1.0
        self.states['siege']['enter'] = self.enter_state_siege
        self.comm_radius = 100
        self.owning_civ.comm_objects.append(self)

        self.buster_display = SimpleSprite(V2(0,0), None)
        self.buster_display.offset = (0.5, 0)
        self.buster_display.layer = 5
        self._generate_buster_display()
        self.scene.game_group.add(self.buster_display)

        self.enter_stealth_time = 1

    def set_starting_busters(self, num):
        self.max_busters = num
        self.busters = num
        self._generate_buster_display()

    def _generate_buster_display(self):
        self.buster_display.image = pygame.Surface((3 * self.max_busters, 3), pygame.SRCALPHA)
        self.buster_display._width, self.buster_display._height = self.buster_display.image.get_size()
        for i in range(self.max_busters):
            pygame.draw.ellipse(self.buster_display.image, PICO_PURPLE, (i*3,0,3,3))
            if i < self.busters:
                self.buster_display.image.set_at((i * 3 + 1, 1), PICO_PINK)
            else:
                self.buster_display.image.set_at((i * 3 + 1, 1), PICO_BLACK)
        self.buster_display._recalc_rect()

    def update(self, dt):
        if self.get_stat("scout_stealth") and not self.stealth:
            self.enter_stealth_time -= dt
            if self.enter_stealth_time < 0:
                self.stealth = True
                self.enter_stealth_time = 10

        self.buster_display.pos = self.pos + V2(0, 4)

        return super().update(dt)

    def fire(self, at):
        super().fire(at)
        self.enter_stealth_time = 10

    def wants_to_dogfight(self):
        if self.stealth:
            return False        
        if not isinstance(self.effective_target, planet.Planet):
            return True
        if not self.effective_target.owning_civ or self.effective_target.owning_civ == self.owning_civ:
            return True
        if (self.effective_target.pos - self.pos).sqr_magnitude() > 100 ** 2:
            return True
        if self.busters <= 0:
            return True
        return False

    def enter_state_siege(self):
        self.buster_time = 1.3

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['shape'] = 'circle'
        mods['size'] = 1
        return mods

    def state_siege(self, dt):
        super().state_siege(dt)
        if self.busters > 0 and isinstance(self.effective_target, planet.Planet):
            self.buster_time -= dt
            if self.buster_time <= 0:
                self.busters -= 1
                self.buster_time = 0.5
                ang = (self.effective_target.pos - self.pos).to_polar()[1]
                rvel = V2.from_angle(ang + 3.14159 + random.random() - 0.5)
                b = bullet.Bullet(
                    self.pos,
                    self.effective_target,
                    self,
                    vel=rvel,
                    mods={
                        'homing':0.5,
                        'color':PICO_PINK,
                        'missile_speed':-0.65,
                        'life':15,
                        'kill_pop':1,
                        'shape':'circle',
                        'size':2,
                        'trail':PICO_PINK
                    }
                )
                self.scene.game_group.add(b)
                self._generate_buster_display()

    def emit_thrust_particles(self):
        pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
        pvel += -self.velocity / 2
        p = particle.Particle([PICO_WHITE, PICO_BLUE], 1, self.pos + -self.velocity.normalized() * self.radius, 2, pvel)
        self.scene.add_particle(p)

    def kill(self):
        self.buster_display.kill()
        return super().kill()
