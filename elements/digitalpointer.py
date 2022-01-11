import math

import pygame
import spritebase
from colors import *
from helper import clamp
import pygame
V2 = pygame.math.Vector2

from elements import arc


class DigitalPointer(spritebase.SpriteBase):
    def __init__(self, pos):
        super().__init__(pos)
        self._offset = (0.5, 0.5)
        self.hover_to_select_t = 0
        self.target = None
        self.mode = None
        self.visible = False
        self.radius = 0
        self.time = 0

    def set_hover(self, target, radius=None, center=None):
        self.target = target
        self.radius = radius or target.collision_radius
        center = center or target.get_center()
        self.pos = center
        self.hover_to_select_t = 0
        self.mode = "hover"
        self.visible = True

    def set_active(self, target, radius=None, center=None):
        self.target = target
        self.radius = radius or target.collision_radius
        center = center or target.get_center()
        self.pos = center
        self.hover_to_select_t = 0
        self.mode = "active"
        self.visible = True

    def set_hidden(self):
        self.visible = False
        self.mode = None

    def _generate_image(self):
        self._width, self._height = (self.radius * 2 + 14, self.radius * 2 + 14)
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        t = self.hover_to_select_t ** 2
        a1 = math.pi * 3 / 4
        a2 = a1 + t * math.pi * 2     
        color = PICO_WHITE if (self.time * 4) % 1 > 0.5 else PICO_LIGHTGRAY   
        if t < 1:
            carrot_size = (1 - t) * 4
            poly = [
                (5,5),
                (4 - carrot_size, 5),
                (5, 4 - carrot_size)
            ]
            
            pygame.draw.polygon(self.image, color, poly, 0)

        if t > 0:
            rect = (5,5,self._width-12,self._height-10)
            t1 = clamp(t * 2,0,1)
            t2 = clamp(t * 2 - 1,0,1)
            pygame.draw.line(self.image, color, (rect[0],rect[1]), (rect[0] + rect[2] * t1, rect[1]))
            pygame.draw.line(self.image, color, (rect[0],rect[1]), (rect[0], rect[1] + rect[3] * t1))
            if t2 > 0:
                pygame.draw.line(self.image, color, (rect[0] + rect[2],rect[1]), (rect[0] + rect[2], rect[1] + rect[3] * t2))
                pygame.draw.line(self.image, color, (rect[0],rect[1] + rect[3]), (rect[0] + rect[2] * t2, rect[1] + rect[3]))
            #pygame.draw.rect(self.image, color, , 1)
            
        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        if self.mode == "active":
            self.hover_to_select_t = clamp(self.hover_to_select_t + dt * 8, 0, 1)
        # TODO: Optimize? Generate only when needed?
        self._generate_image()
        return super().update(dt)
