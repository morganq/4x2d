import pygame
from resources import resource_path
import spritebase

class SimpleSprite(spritebase.SpriteBase):
    def __init__(self, pos, img=None):
        spritebase.SpriteBase.__init__(self, pos)
        if isinstance(img, str):
            try:
                self.image = pygame.image.load(resource_path(img)).convert_alpha()
            except:
                self.image = pygame.Surface((1,1))
                print("BAD IMAGE: %s" % img)
        else:
            self.image = img
        self._width = 1
        self._height = 1
        if self.image:
            self._width = self.image.get_rect()[2]
            self._height = self.image.get_rect()[3]
        self._recalc_rect()