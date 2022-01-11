import random

import helper
import pygame
from colors import *
from particle import Particle
from rangeindicator import RangeIndicator
from spaceobject import SpaceObject

V2 = pygame.math.Vector2


class Alien3Void(SpaceObject):
    def __init__(self, scene, attached, radius, color=PICO_BLACK):
        super().__init__(scene, attached.pos)
        self.attached = attached
        self.radius = radius
        self._layer = -1
        self.color = color
        self._generate_image()
        self.offset = (0.5,0.5)
        self.target_radius = self.radius
        self.ring = RangeIndicator(self.pos, self.radius + 1.5, self.color, 2, 5)
        self.ring._layer = -2
        self.scene.game_group.add(self.ring)

    def _generate_image(self):
        r = int(self.radius)
        self._width = r * 2
        self._height = r * 2
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PICO_BLACK, (r,r), r, 0)
        num = r
        #for i in range(num):
        #    theta = i / (num-1) * 6.2818
        #    p = helper.from_angle(theta) * r
        #    self.image.set_at((p + V2(r, r)), PICO_LIGHTGRAY)

        self._recalc_rect()

    def grow(self):
        if self.radius < 50:
            self.target_radius = self.radius + 10
        elif self.radius < 80:
            self.target_radius = self.radius + 5

    def update(self, dt):
        self.pos = self.attached.pos
        self.ring.pos = self.attached.pos
        if self.radius < self.target_radius:
            self.radius += 1 * dt
            self._generate_image()
            self.ring.radius = self.radius + 1.5
            self.ring._generate_image()
        
        if random.random() > 0.93:
            pos = helper.random_angle() * random.random() * self.radius + self.pos
            p = Particle([PICO_LIGHTGRAY, PICO_DARKGRAY], 1, pos, 0.25, helper.random_angle() * 3)
            p._layer = -1
            self.scene.game_group.add(p)

        return super().update(dt)

    def kill(self):
        self.ring.kill()
        return super().kill()
