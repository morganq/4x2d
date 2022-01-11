import math

import pygame
from colors import *
from helper import clamp
from spritebase import SpriteBase
import pygame
V2 = pygame.math.Vector2


class RewindParticle(SpriteBase):
    def __init__(self, pos, radius):
        super().__init__(pos)
        self.radius = radius + 5
        self.offset = (0.5, 0.5)
        self.time = 0 
        self._generate_image()

    def _generate_image(self):
        self._width, self._height = self.radius * 2 + 8, self.radius * 2 + 8
        t1 = math.cos(clamp(self.time, 0, 1) * 3.14159) * -0.5 + 0.5
        t2 = math.cos(clamp(self.time - 0.65, 0, 1) * 3.14159) * -0.5 + 0.5
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        a1 = 3.14159 / 2 + t2 * 6.2818
        a2 = 3.14159 / 2 + t1 * 6.4
        #pygame.draw.arc(self.image, PICO_BLUE, (4,4,self._width - 8, self._height - 8), a1, a2, 1)
        center = V2(self._width / 2, self._height / 2)
        pts = []
        steps = int(a2 * 20)
        for i in range(steps):
            theta = i / 20
            if theta > a1:
                pts.append((helper.from_angle(-theta) * self.radius + center - V2(1,1)))
        if len(pts) >= 2:
            pygame.draw.lines(self.image, PICO_BLUE, False, pts, 2)
        vs = helper.from_angle(-a2)
        vf = V2(vs.y, -vs.x)
        
        pt = vs * self.radius + center
        p1 = pt + vs * 3 + vf * -3
        p2 = pt + -vs * 3 + vf * -3
        pygame.draw.lines(self.image, PICO_BLUE, False, [tuple(p1), pt, tuple(p2)], 2)

        self._recalc_rect()

    def update(self, dt):
        self.time += dt * 1.6
        self._generate_image()
        if self.time > 1.65:
            self.kill()
        return super().update(dt)
