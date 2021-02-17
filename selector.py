from spritebase import SpriteBase
import pygame
from colors import *

class Selector(SpriteBase):
    def __init__(self, object):
        self.object = object
        SpriteBase.__init__(self, object.pos)
        self.offset = (0.5, 0.5)
        self._generate_image()

    def change_selection(self, object):
        self.object = object
        self._generate_image()
        self.pos = object.pos

    def _generate_image(self):
        w = self.object.selection_radius * 2
        h = self.object.selection_radius * 1
        h2 = h * 2
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, PICO_WHITE, (0,-(h2-h)/2, w, h2), 1)
        self._width = w
        self._height = h
        self._recalc_rect()