import pygame

import game
from helper import clamp
from spritebase import SpriteBase
import pygame
V2 = pygame.math.Vector2


class ScrollPanel(SpriteBase):
    def __init__(self, pos, size):
        super().__init__(pos)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self._width, self._height = size
        self._recalc_rect()
        self.selectable = True
        self.click_pos = None

    def on_drag(self, pos):
        delta = pos - self.click_pos
        self.scroll(self.pos + delta)
        return super().on_drag(pos)

    def on_mouse_down(self, pos):
        self.click_pos = pos
        return super().on_mouse_down(pos)

    def scroll(self, pos):
        self.pos = V2(
            clamp(pos.x, - self._width + game.Game.inst.game_resolution.x, 0),
            clamp(pos.y, - self._height + game.Game.inst.game_resolution.y, 0)
        )
