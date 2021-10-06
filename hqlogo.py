import math

import pygame

import spritebase
import text
from colors import *
from helper import clamp
from v2 import V2


class HQLogo(spritebase.SpriteBase):
    def __init__(self, pos):
        super().__init__(pos)
        self.line1 = "HOSTILE"
        self.line2 = "QUADRANT"
        self.time = 0
        self._generate_image()

    def _draw_text(self, surf, s, color, pos, width):
        for i,char in enumerate(s):
            cs = text.render_multiline(char, "logo", color)
            csw, csh = cs.get_size()
            # split the width into (chars * 2) pieces
            tx = width / (len(s) * 2) * (i * 2 + 1) + pos.x
            surf.blit(cs, (tx - csw / 2, pos.y))

    def _generate_image(self):
        z = clamp((self.time) * 1.5, 0, 1)
        t = 1 - ((1 - z) ** 2)
        self._width = 120 + t * 200
        self._height = 100
        self.image = pygame.Surface((self._width + 20, self._height), pygame.SRCALPHA)
        color1 = PICO_DARKGRAY
        color2 = PICO_DARKGRAY
        if self.time > 0.6:
            color1 = PICO_RED
            color2 = PICO_WHITE
        self._draw_text(self.image, self.line1, color1, V2(10, 0), self._width)
        self._draw_text(self.image, self.line2, color2, V2(10, 35), self._width)
        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        if self.time < 4:
            self._generate_image()
        return super().update(dt)
