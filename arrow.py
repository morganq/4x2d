from spritebase import SpriteBase
from colors import *
from v2 import V2
from line import ptmax, ptmin
import pygame
import game

class OrderArrow(SpriteBase):
    def __init__(self):
        SpriteBase.__init__(self, V2(0,0))
        self._layer = -1

    def setup(self, start_planet, end, end_planet=None):
        thickness = 6
        ht = thickness / 2
        color = PICO_LIGHTGRAY
        end_offset = 0
        start_offset = 20
        if end_planet:
            end = end_planet.pos
            color = PICO_WHITE
            end_offset = 20
        pt1 = start_planet.pos
        pt2 = end
        delta = pt2 - pt1

        if delta.sqr_magnitude() < 25 ** 2:
            self.visible = False
            return

        self.visible = True

        w = game.RES[0]
        h = game.RES[1]

        forward = delta.normalized()
        side = V2(forward.y, -forward.x)
        pt1 += forward * start_offset
        pt2 += forward * -end_offset
        points = []
        points.append(pt1 + side * -ht)
        points.append(pt1 + side * ht)
        points.append(pt2 + side * ht + forward * -15)
        points.append(pt2 + side * 15 + forward * -15)
        points.append(pt2)
        points.append(pt2 + side * -15 + forward * -15)
        points.append(pt2 + side * -ht + forward * -15)
        points = [p.tuple() for p in points]

        arrow1 = pt2 + forward * - 10 + side * 10
        arrow2 = pt2 + forward * - 10 + side * -10        

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, points, 0)
        self._width = w
        self._height = h

        self.pos = V2(0,0)
        self._recalc_rect()