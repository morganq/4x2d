import pygame

import helper
from colors import *
from spaceobject import SpaceObject

V2 = pygame.math.Vector2
import random


class Hazard(SpaceObject):
    def __init__(self, scene, pos, size):
        self.size = size
        super().__init__(scene, pos)
        self.collidable = True
        self.stationary = True        
        self.radius = self.get_radius()
        self.collision_radius = self.radius

        self._generate_image()

    def get_radius(self):
        return self.size + 8

    def _generate_image(self):
        r = self.get_radius()
        self._width = r * 2 + 12
        self._height = r * 2 + 12
        center = V2(r + 6, r + 6)
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        circles = []
        for i in range(self.radius // 2 + 2):
            pos = helper.from_angle(random.random() * 6.2818) * (random.random() * (self.radius * 1) + 1)
            size = 1
            if pos.length_squared() > (self.radius * 0.75) ** 2:
                size = random.random() * 2 + 1
            else:
                size = random.random() * 6 + 3
            
            circles.append((pos, size))

        for circle in circles:
            pygame.draw.circle(self.image, PICO_BLACK, (circle[0] + center + V2(0,1)), circle[1], 0)
        for circle in circles:
            pygame.draw.circle(self.image, PICO_DARKGRAY, (circle[0] + center), circle[1], 0)
        for circle in circles:            
            pygame.draw.circle(self.image, PICO_LIGHTGRAY, (circle[0] + center + V2(-1,-1)), circle[1]-1, 0)
        for circle in circles:
            if circle[1] > 4:
                pygame.draw.circle(self.image, PICO_WHITE, (circle[0] + center + V2(-1,-3)), circle[1]-4, 0)            

        #pygame.draw.circle(self.image, PICO_PINK, center, r, 1)
        self._recalc_rect()
