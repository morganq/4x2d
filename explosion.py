import math

import pygame

from helper import clamp
from particle import Particle
from spritebase import SpriteBase


class Explosion(SpriteBase):
    def __init__(self, pos, colors, lifetime, max_size, scale_fn=None, line_width=1.5):
        super().__init__(pos)
        self.colors = colors
        self.lifetime = lifetime
        self.max_size = max_size
        self.line_width = line_width
        if isinstance(scale_fn, str):
            self.scale_fn = {
                "log":lambda t:clamp(math.log(t * 10+1) / 4 + t / 2.5, 0, 1)
            }[scale_fn]
        else:
            self.scale_fn = scale_fn or (lambda t:t)
        self.time = 0
        self.image = pygame.Surface((self.max_size * 2, self.max_size * 2), pygame.SRCALPHA)
        self._width,self._height = self.max_size * 2, self.max_size * 2
        self._offset = (0.5, 0.5)
        self._recalc_rect()
        self.generate_image()


    def generate_image(self):
        t = min(self.time / self.lifetime,1)
        ci = clamp(int(len(self.colors) * t), 0, len(self.colors) - 1)
        size = self.scale_fn(t) * self.max_size
        temp = pygame.Surface((self.max_size * 2, self.max_size * 2), pygame.SRCALPHA)
        if t <= 1:
            pygame.draw.circle(temp, self.colors[ci], (self.max_size, self.max_size), size, 0)
        temp.blit(self.image, (0,0))
        innersize = clamp(size - self.line_width, 0, 999)
        pygame.draw.circle(temp, (0,0,0,0), (self.max_size, self.max_size), innersize, 0)
        self.size = size
        self.image = temp

    def update(self, dt):
        self.time += dt
        if self.time > (self.lifetime * 2):
            self.kill()
        self.generate_image()
        return super().update(dt)
