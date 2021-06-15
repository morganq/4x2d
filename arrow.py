from spritebase import SpriteBase
from colors import *
from v2 import V2
from line import ptmax, ptmin
import pygame
import game
import sound

class Arrow(SpriteBase):
    def __init__(self, pt1, pt2, color):
        super().__init__(pt1)
        self.pt1 = pt1
        self.pt2 = pt2
        self.color = color
        self._generate_image()

    def _generate_image(self):
        thickness = 6
        ht = thickness / 2
        color = self.color
        delta = self.pt2 - self.pt1
        pt1 = self.pt1.copy()
        pt2 = self.pt2.copy()

        w = game.RES[0] #TODO: wat. 
        h = game.RES[1]

        forward = delta.normalized()
        side = V2(forward.y, -forward.x)
        points = []
        points.append(pt1 + side * -ht)
        points.append(pt1 + side * ht)
        points.append(pt2 + side * ht + forward * -15)
        points.append(pt2 + side * 15 + forward * -15)
        points.append(pt2)
        points.append(pt2 + side * -15 + forward * -15)
        points.append(pt2 + side * -ht + forward * -15)
        points = [p.tuple() for p in points]

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, points, 0)
        self._width = w
        self._height = h

        self.pos = V2(0,0)
        self._recalc_rect()

class OrderArrow(SpriteBase):
    def __init__(self):
        SpriteBase.__init__(self, V2(0,0))
        self._layer = -1
        self.last_end = None

    def setup(self, start_planet, end, end_planet=None):
        thickness = 6
        ht = thickness / 2
        color = PICO_LIGHTGRAY
        end_offset = 0
        start_offset = 20
        if end_planet:
            end = end_planet.pos
            color = PICO_WHITE
            end_offset = (end_planet.radius + 6)
        pt1 = start_planet.pos
        pt2 = end
        if not end:
            self.visible = False
            return
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

        if self.last_end is None:
            self.last_end = end

        if (end - self.last_end).sqr_magnitude() > 10 ** 2:
            if end_planet:
                sound.play("short2")
            else:
                sound.play("short1")
            self.last_end = end        