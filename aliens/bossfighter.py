import random

import helper
import pygame
import sound
from bullet import Bullet
from colors import *
from particle import Particle
from ships.all_ships import register_ship
from ships.fighter import Fighter

V2 = pygame.math.Vector2


@register_ship
class BossFighter(Fighter):
    SHIP_NAME = "bossfighter"
    DISPLAY_NAME = "Censor Fighter"
    BASE_HEALTH = 25
    BASE_DAMAGE = 3
    FIRE_RATE = 0.65
    MAX_SPEED = 10
    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/bossfighter.png", 13)
        self.fast_fire_timer = 0
        self.bullets_chambered = 0
        self.firing_target = None

    def special_fire(self, at):
        towards = helper.try_normalize(at.pos - self.pos)

        fwd = helper.try_normalize(self.velocity)
        side = V2(fwd.y, -fwd.x)
        coef = (self.bullets_chambered % 2) * 2 - 1
        b = Bullet(self.pos + side * coef * 2, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        sound.play(random.choice(['laser1', 'laser2', 'laser3']))

        self.pos += -towards * 1

        for i in range(7):
            pvel = helper.try_normalize(towards + V2(random.random() * 0.75, random.random() * 0.75)) * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_YELLOW, PICO_RED, PICO_PURPLE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.add_particle(p)

        self.bullets_chambered -= 1

    def fire(self, at):
        self.bullets_chambered = 2
        self.firing_target = at
        self.fast_fire_timer = 0
        self.special_fire(at)

    def update(self, dt):
        if self.bullets_chambered > 0:
            self.fast_fire_timer += dt
            if self.fast_fire_timer > 0.3:
                self.fast_fire_timer = 0
                self.special_fire(self.firing_target)
        return super().update(dt)
