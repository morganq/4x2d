from spritebase import SpriteBase
from resources import resource_path
from v2 import V2
import text
import pygame
from colors import *

class IconText(SpriteBase):
    def __init__(self, pos, icon, text, color):
        SpriteBase.__init__(self, pos)
        if icon:
            self.icon = pygame.image.load(resource_path(icon)).convert_alpha()
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
            self._height = self.icon.get_height()
        else:
            self._width = tr[2]
            self._height = tr[3] + 1
        
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        if self.icon:
            self.image.blit(self.icon, (0,0))
            text.FONTS['tiny'].render_to(self.image, (self.icon.get_width() + 2, 4), self.text, PICO_BLACK)
            text.FONTS['tiny'].render_to(self.image, (self.icon.get_width() + 2, 3), self.text, self.color)
        else:
            text.FONTS['tiny'].render_to(self.image, (0, 1), self.text, PICO_BLACK)
            text.FONTS['tiny'].render_to(self.image, (0, 0), self.text, self.color)
        self._recalc_rect()

    def update(self, dt):
        self.pos += V2(0, (-dt * 25) / (self.time + 1))
        self.time += dt
        if self.time > 1.5:
            self.kill()