import math
import random

import pygame
from colors import *
from v2 import V2
from helper import get_nearest
from spaceobject import SpaceObject
from icontext import IconText
import economy

class Asteroid(SpaceObject):
    HEALTHBAR_SIZE = (20, 2)
    def __init__(self, scene, pos, resources):
        super().__init__(scene, pos)
        self.resources = resources
        self.total_resources = (self.resources.iron + self.resources.ice + self.resources.gas)
        self.radius = self.total_resources // 30 + 2
        self.offset = (0.5, 0.5)
        self.selectable = True
        self.collidable = True
        self.stationary = True
        self.collision_radius = self.radius + 4
        self.set_health(self.get_max_health())
        self._circles = []

        for i in range(self.total_resources // 20 + 2):
            pos = V2.from_angle(random.random() * 6.2818) * (random.random() * (self.radius * 0.75) + 1)
            size = 1
            if pos.sqr_magnitude() > (self.radius * 0.75) ** 2:
                size = random.random() * 2 + 1
            else:
                size = random.random() * 4 + 2
            
            self._circles.append((pos, size))
        self._generate_frames()
        self.health_bar.pos = self.pos + V2(0, -7)

    def get_max_health(self):
        return self.total_resources * 0.75

    def _generate_frame(self, border=False):
        w = self.radius * 2 + 16
        h = w
        image = pygame.Surface((w,h), pygame.SRCALPHA)

        offset = V2(w/2,h/2)
        for (pos, size) in self._circles:
            pygame.draw.circle(image, PICO_YELLOW, (pos + offset).tuple(), size + (2 if border else 1), 0) 
        for (pos, size) in self._circles:
            pygame.draw.circle(image, PICO_RED, (pos + offset).tuple(), size, 0)
        for (pos, size) in self._circles:
            pygame.draw.circle(image, PICO_ORANGE, (pos + offset + V2(-1,-1)).tuple(), size-1, 0)            
        for (pos, size) in self._circles:
            if size > 3:
                pygame.draw.circle(image, PICO_YELLOW, (pos + offset + V2(-1,-3)).tuple(), size - 3, 0)            

        #pygame.draw.circle(image, PICO_WHITE, V2(w/2,h/2).tuple(), self.radius, 1)

        return image

    def _generate_frames(self):
        inactive = self._generate_frame(False)
        hover = self._generate_frame(True)
        w = inactive.get_width()
        h = inactive.get_height()
        self._sheet = pygame.Surface((w * 2, h), pygame.SRCALPHA)
        self._sheet.blit(inactive, (0,0))
        self._sheet.blit(hover, (w,0))
        self._width = w
        self._height = h
        self._frame_width = w
        self._recalc_rect()
        self._update_image()

    def on_mouse_enter(self, pos):
        self.frame = 1
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self.frame = 0
        return super().on_mouse_exit(pos)

    def get_selection_info(self):
        return {"type":"asteroid","asteroid":self}        

    def take_damage(self, damage, origin):
        super().take_damage(damage, origin=origin)

        if self.health <= 0:
            civ = origin.owning_civ
            for r,v in self.resources.data.items():
                yield_mul = civ.get_stat("asteroid_yield_mul") + 1
                v *= yield_mul
                civ.earn_resource(r, v, where=self.pos)
            self.kill()