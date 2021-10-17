import math

import pygame
import spritebase
import text
from colors import *
from helper import clamp
from v2 import V2


class ExpandingText(spritebase.SpriteBase):
    def __init__(self, pos, line, time=0.75, color=PICO_WHITE):
        super().__init__(pos)
        self.line = line
        self.time = 0
        self.rate = time
        self.base_width = len(line) * 17
        self.color = color
        self._generate_image()

    def _draw_text(self, surf, s, color, pos, width):
        for i,char in enumerate(s):
            cs = text.render_multiline(char, "logo", color)
            csw, csh = cs.get_size()
            # split the width into (chars * 2) pieces
            tx = width / (len(s) * 2) * (i * 2 + 1) + pos.x
            surf.blit(cs, (tx - csw / 2, pos.y))

    def _generate_image(self):
        z = clamp((self.time) / self.rate, 0, 1)
        t = 1 - ((1 - z) ** 2)
        self._width = self.base_width + t * 200
        self._height = 100
        self.image = pygame.Surface((self._width + 20, self._height), pygame.SRCALPHA)
        self._draw_text(self.image, self.line, self.color, V2(10, 0), self._width)
        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        if self.time < (self.time * self.rate + 1):
            self._generate_image()
        return super().update(dt)
