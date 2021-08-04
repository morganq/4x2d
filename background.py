import math
import random

import pygame

import game
from colors import *
from helper import clamp
from spritebase import SpriteBase


class Background(SpriteBase):
    def __init__(self, pos, gridsize=20, size=None):
        SpriteBase.__init__(self, pos)
        self.gridsize = gridsize
        self.time = 0
        self.stars = []
        self.size = size or game.RES
        for i in range(90):
            self.stars.append((random.randint(0, game.RES[0]),random.randint(0, game.RES[1])))
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)

        for star in self.stars:
            self.image.set_at(star, PICO_LIGHTGRAY)        

        GS = self.gridsize
        ss = GS / 20
        ix = self.size[0] // GS
        iy = self.size[1] // GS
        for i in range(ix):
            for j in range(iy):
                x = int(i * GS + GS / 2)
                y = int(j * GS + GS / 2)
                xt = x + self.time * 30
                colors = [PICO_DARKGRAY, PICO_DARKBLUE, PICO_PURPLE]
                colorf = math.sin(pow(xt / 175 * ss, 1.8) + y / 30) * 1.25 + 1.5
                #colorf = y / game.RES[1] * 3
                color = colors[int(colorf)]
                linelenf = math.sin(-xt / 31 * ss + pow(y/80,2)) * 0.65 + 1.75
                linelenf *= ss
                lineleni = min(int(linelenf),4)
                pygame.draw.line(self.image, color, (x - lineleni, y), (x + lineleni, y), 1)
                pygame.draw.line(self.image, color, (x, y - lineleni), (x, y + lineleni), 1)
                off = clamp(math.sin(xt / 90 * ss + pow(-y/10,2)) * 6 + 12,0, 10) * ss
                if off < 10 * ss and random.random() > 0.5:
                    pygame.draw.line(self.image, color, (x + off, y), (x + GS - off, y), 1)
                    pygame.draw.line(self.image, color, (x - off, y), (x - GS + off, y), 1)
                    pygame.draw.line(self.image, color, (x, y + off), (x, y + GS - off), 1)
                    pygame.draw.line(self.image, color, (x, y - off), (x, y - GS + off), 1)

        self._width = game.RES[0]
        self._height = game.RES[1]
        self._recalc_rect()

    def update(self, dt):
        #self.time += dt
        #if (self.time + dt) % 3 < self.time % 3:
        #self._generate_image()
        return super().update(dt)
