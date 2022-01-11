import random

import pygame
import pygame.gfxdraw
from colors import *
from helper import clamp
from resources import resource_path
from spritebase import SpriteBase
import pygame
V2 = pygame.math.Vector2


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
        direction = delta.normalize()
        center = V2(w / 2,h / 2)
        distance = delta.length()
        steps = int((distance - 40) / 8)
        
        time_offset = (self.time * 1) % 1

        extra = 2 if self.current else 1


        color = PICO_ORANGE
        if self.travelled:
            color = PICO_GREEN
        if self.current:
            color = PICO_WHITE

        pygame.draw.line(self.image, color,
            (center - direction * (distance - 28) / 2),
            (center + direction * (distance - 28) / 2),
            2
        )

        self._width = w
        self._height = h
        self._recalc_rect()
