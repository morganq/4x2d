import pygame
from resources import resource_path
from v2 import V2
from colors import *
import text
from spritebase import SpriteBase

class ShipCounter(SpriteBase):
    def __init__(self, planet):
        super().__init__(V2(0,0))
        self.planet = planet
        self._num_ships = 0
        self._generate_image()
        self.visible = False
        self.pos = planet.pos + V2(3,3)

    def _generate_image(self):
        r = 8
        w = r*2 + 6
        h = r*2
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PICO_PURPLE, (5,6),5, 0)
        pygame.draw.circle(self.image, PICO_PURPLE, (3 + r,r),r, 0)
        img = pygame.image.load(resource_path("assets/i-fighter.png")).convert_alpha()
        self.image.blit(img, (-2, 0))
        s = str(int(self._num_ships))
        tr = text.FONTS['small'].get_rect(s)
        text.FONTS['small'].render_to(self.image, (r - tr[2]/2 + 4, r - tr[3]/2), s, PICO_GREEN)
        self._width = w
        self._height = h
        self._recalc_rect()

    def update(self, dt):
        if self.planet.ships['fighter'] != self._num_ships:
            self._num_ships = self.planet.ships['fighter']
            self._generate_image()
            if self._num_ships == 0:
                self.visible = False
            else:
                self.visible = True
        return super().update(dt)