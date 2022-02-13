import math

import pygame
import text
from colors import *
from elements import arc
from helper import clamp
from resources import resource_path
from spritebase import SpriteBase


class PopPctCircle(SpriteBase):
    def __init__(self, planet):
        super().__init__(pygame.Vector2(0,0))
        self.planet = planet
        
        self.visible = False
        self.pos = planet.pos
        self.time = 0
        self.layer = -1
        self.offset = (0.5, 0.5)
        self.interp_value = 0
        self._generate_image()

    def _generate_image(self):
        rad = self.planet.get_radius()
        self._width = rad * 2 + 4
        self._height = self._width
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        a1 = -math.pi / 2
        a2 = a1 + self.interp_value * 6.2818
        pygame.draw.circle(self.image, PICO_BLACK, (self._width // 2, self._height // 2), rad + 2, 5)
        if a2 > a1:
            arc.draw_arc(self.image, PICO_YELLOW, (self._width // 2, self._height // 2), rad + 3, a1, a2, 5)

        self._recalc_rect()

    def update(self, dt):
        if self.planet.owning_civ is None or not self.planet.owning_civ.is_player:
            self.visible = False
        else:
            self.visible = True

        if self.visible:
            target_interp = clamp(self.planet.population / self.planet.get_max_pop(), 0, 1)
            if target_interp < self.interp_value:
                self.interp_value = clamp(self.interp_value - dt * 0.5, target_interp, 1)
                self._generate_image()
            elif target_interp > self.interp_value:
                self.interp_value = clamp(self.interp_value + dt * 0.5, 0, target_interp)
                self._generate_image()
        return super().update(dt)
        