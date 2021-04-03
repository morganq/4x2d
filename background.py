from colors import *
from spritebase import SpriteBase
import pygame
import game
import random
import math

class Background(SpriteBase):
    def __init__(self, pos, gridsize=20):
        SpriteBase.__init__(self, pos)
        self.gridsize = gridsize
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface(game.RES, pygame.SRCALPHA)

        for i in range(90):
            self.image.set_at((random.randint(0, game.RES[0]),random.randint(0, game.RES[1])), PICO_LIGHTGRAY)        

        GS = self.gridsize
        ss = GS / 20
        ix = game.RES[0] // GS
        iy = game.RES[1] // GS
        for i in range(ix):
            for j in range(iy):
                x = int(i * GS + GS / 2)
                y = int(j * GS + GS / 2)
                colors = [PICO_DARKGRAY, PICO_DARKBLUE, PICO_PURPLE]
                colorf = math.sin(pow(x / 175 * ss, 1.8) + y / 30) * 1.25 + 1.5
                #colorf = y / game.RES[1] * 3
                color = colors[int(colorf)]
                linelenf = math.sin(-x / 31 * ss + pow(y/80,2)) * 0.65 + 1.75
                linelenf *= ss
                lineleni = min(int(linelenf),2)
                pygame.draw.line(self.image, color, (x - lineleni, y), (x + lineleni, y), 1)
                pygame.draw.line(self.image, color, (x, y - lineleni), (x, y + lineleni), 1)
                if random.random() > 0.9:
                    off = ss * 8
                    pygame.draw.line(self.image, color, (x + off, y), (x + GS - off, y), 1)
                    pygame.draw.line(self.image, color, (x - off, y), (x - GS + off, y), 1)
                    pygame.draw.line(self.image, color, (x, y + off), (x, y + GS - off), 1)
                    pygame.draw.line(self.image, color, (x, y - off), (x, y - GS + off), 1)

        self._width = game.RES[0]
        self._height = game.RES[1]
        self._recalc_rect()