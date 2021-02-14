import pygame
from resources import resource_path
import spritebase

class SimpleSprite(spritebase.SpriteBase):
    def __init__(self, img, pos):
        spritebase.SpriteBase.__init__(self, pos)
        self.image = pygame.image.load(resource_path(img)).convert_alpha()
        self._width = self.image.get_rect()[2]
        self._height = self.image.get_rect()[3]
        self._recalc_rect()