import pygame
import pygame.gfxdraw
from resources import resource_path
from v2 import V2
import random
from helper import clamp
from colors import *
from spritebase import SpriteBase

class StarPath(SpriteBase):
    def __init__(self, pos1, pos2, travelled = False, current = False):
        self.pos1 = pos1
        self.pos2 = pos2
        self.travelled = travelled
        self.current = current
        self.time = 0
        super().__init__((self.pos1 + self.pos2) / 2)
        self.offset = (0.5, 0.5)
        self._generate_image()

    def update(self, dt):
        self.time += dt
        if self.current:
            self._generate_image()
        return super().update(dt)

    def _generate_image(self):
        delta = self.pos2 - self.pos1
        w = abs(int(delta.x)) + 32
        h = abs(int(delta.y)) + 32
        
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)        
        direction = delta.normalized()
        center = V2(w / 2,h / 2)
        distance = delta.magnitude()
        steps = int((distance - 40) / 8)
        
        time_offset = (self.time * 1) % 1

        extra = 2 if self.current else 1

        for i in range(steps + extra):
            p = (i - steps / 2) * direction * 8 + center + ((time_offset + 1 - extra) * 8) * direction
            color = PICO_BROWN
            if self.travelled:
                color = PICO_GREEN
            radius = 3
            if self.current:
                color = PICO_LIGHTGRAY
                x = distance / 2 - 10 - (center - p).magnitude()
                radius = clamp(x / 3,1,3)
            pygame.draw.circle(self.image, color, p.tuple_int(),radius, 1)

        # pygame.draw.rect(self.image, PICO_PINK, (0,0,w,h), 1)

        self._width = w
        self._height = h
        self._recalc_rect()