import pygame

import text
from colors import *
from resources import resource_path
from spritebase import SpriteBase
import pygame
V2 = pygame.math.Vector2


class IconText(SpriteBase):
    def __init__(self, pos, icon, text, color):
        SpriteBase.__init__(self, pos + V2(0,-2))
        if icon:
            try:
                self.icon = pygame.image.load(resource_path(icon)).convert_alpha()
            except:
                print("BAD ICON: %s" % icon)
                self.icon = None
        else:
            self.icon = None
        self.text = text
        self.color = color
        self.offset = (0.5,0.5)
        self._generate_image()
        self.time = 0
        self.layer = -1

    def _generate_image(self):
        tr = text.FONTS['tiny'].get_rect(self.text)
        if self.icon:
            self._width = tr[2] + 4 + self.icon.get_width()
            self._height = max(self.icon.get_height(), tr[3] + 3)
        else:
            self._width = tr[2]
            self._height = tr[3] + 1
        
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        if self.icon:
            self.image.blit(self.icon, (0,2))
            text.FONTS['tiny'].render_to(self.image, (self.icon.get_width() + 2, 1), self.text, PICO_BLACK)
            text.FONTS['tiny'].render_to(self.image, (self.icon.get_width() + 2, 0), self.text, self.color)
        else:
            text.FONTS['tiny'].render_to(self.image, (0, 1), self.text, PICO_BLACK)
            text.FONTS['tiny'].render_to(self.image, (0, 0), self.text, self.color)
        self._recalc_rect()

    def update(self, dt):
        self.pos += V2(0, (-dt * 18) / (self.time + 1))
        self.time += dt
        if self.time > 1.66:
            self.kill()
