import pygame

import game
from spritebase import SpriteBase
from v2 import V2


class PauseOverlay(SpriteBase):
    def __init__(self):
        super().__init__(V2(0,0))
        self.visible = False
        self._exceptions = []
        self._generate_image()

    def set_exceptions(self, exceptions):
        self._exceptions = exceptions
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface(game.Game.inst.game_resolution.tuple_int(), pygame.SRCALPHA)
        self.image.fill((0,0,0,80))
        for spr in self._exceptions:
            mask = pygame.mask.from_surface(spr.image,)
            mask.to_surface(self.image, setcolor=(0,0,0,0), unsetcolor=(0,0,0,80), dest=spr.rect)
        self._width, self._height = self.image.get_size()
        self._recalc_rect()

    def update(self, dt):
        if self.visible:
            self._generate_image()
        return super().update(dt)
