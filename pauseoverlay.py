import pygame

import game
from spritebase import SpriteBase
import pygame
V2 = pygame.math.Vector2


class PauseOverlay(SpriteBase):
    def __init__(self):
        super().__init__(V2(0,0))
        self.visible = False
        self._exceptions = []
        self.darkness = 80
        self._generate_image()

    def set_exceptions(self, exceptions):
        self._exceptions = exceptions
        self._generate_image()

    def darken(self):
        self.darkness = 160
        self._generate_image(160)


    def _generate_image(self, darkness=80):
        self.image = pygame.Surface(game.tuple(Game.inst.game_resolution), pygame.SRCALPHA)
        self.image.fill((0,0,0,darkness))
        for spr in self._exceptions:
            mask = pygame.mask.from_surface(spr.image,)
            mask.to_surface(self.image, setcolor=(0,0,0,0), unsetcolor=(0,0,0,darkness), dest=spr.rect)
        self._width, self._height = self.image.get_size()
        self._recalc_rect()

    def update(self, dt):
        if self.visible:
            self._generate_image(self.darkness)
        return super().update(dt)
