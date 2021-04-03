from spritebase import SpriteBase
import pygame
from helper import clamp

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
        self.pos += delta
        return super().on_drag(pos)

    def on_mouse_down(self, pos):
        self.click_pos = pos
        return super().on_mouse_down(pos)