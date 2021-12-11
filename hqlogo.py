import math

import pygame

import spritebase
import text
from colors import *
from helper import clamp
from v2 import V2


class HQLogo(spritebase.SpriteBase):
    def __init__(self, pos, delay=0):
        super().__init__(pos)
        self.line1 = "HOSTILE"
        self.line2 = "QUADRANT"
        self.time = -delay
        self._generate_image()

    def _draw_text(self, surf, s, color, pos, width):
        for i,char in enumerate(s):
            csb = text.render_multiline(char, "logo", PICO_WHITE)
            cs = text.render_multiline(char, "logo", color)
            csw, csh = cs.get_size()
            # split the width into (chars * 2) pieces
            tx = width / (len(s) * 2) * (i * 2 + 1) + pos.x
            surf.blit(csb, (tx - csw / 2, pos.y + 1))
            surf.blit(csb, (tx - csw / 2, pos.y - 1))
            surf.blit(csb, (tx - csw / 2 - 1, pos.y))
            surf.blit(csb, (tx - csw / 2 + 1, pos.y))
            surf.blit(cs, (tx - csw / 2, pos.y))

    def _generate_image(self):
        z = clamp((self.time) * 1.5, 0, 1)
        t = 1 - ((1 - z) ** 2)
        self._width = 60 + t * 100
        self._height = 50
        self.image = pygame.Surface((self._width + 20, self._height), pygame.SRCALPHA)
        color1 = PICO_WHITE
        color2 = PICO_WHITE
        if self.time > 0.6:
            color1 = PICO_RED
            color2 = PICO_BLACK
        self._draw_text(self.image, self.line1, color1, V2(10, 1), self._width)
        self._draw_text(self.image, self.line2, color2, V2(10, 25), self._width)
        self._recalc_rect()

    def update(self, dt):
        if self.time < 0:
            self.visible = False
        else:
            self.visible = True
        self.time += dt * 0.9
        if self.time < 4:
            self._generate_image()
        return super().update(dt)
