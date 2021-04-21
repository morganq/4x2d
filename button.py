import pygame
from colors import *
from spritebase import SpriteBase
import text
from fadeinmixin import FadeInMixin

SIZE_PADDING = {'tiny':4, 'small':7, 'medium':10, 'big':12, 'huge':18}
HEIGHTS = {'tiny':5, 'small':7, 'medium':16, 'big':10, 'huge':15}

class Button(SpriteBase, FadeInMixin):
    def __init__(self, pos, text, size, onclick):
        SpriteBase.__init__(self, pos)
        self.color = PICO_WHITE
        self.text = text
        self.size = size
        self.onclick = onclick
        self.selectable = True
        self._generate_image()

    def _generate_image(self, hover=False):
        tw = text.FONTS[self.size].get_rect(self.text)
        
        pad = SIZE_PADDING[self.size]
        w = tw[2] + pad * 2
        h = HEIGHTS[self.size] + pad * 2
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, self.color, (0,0,w,h), 1)
        if hover:
            pygame.draw.rect(self.image, self.color, (1,1,w-2,h-2), 0)
            text_color = PICO_RED
        else:
            pygame.draw.rect(self.image, self.color, (2,2,w-4,h-4), 0)
            text_color = PICO_BLACK
        
        text.FONTS[self.size].render_to(self.image, (w / 2 - tw[2] / 2, pad), self.text, text_color)

        self._width = w
        self._height = h
        self._recalc_rect()

    def on_mouse_enter(self, pos):
        self._generate_image(True)
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self._generate_image(False)
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        self.onclick()
        self._generate_image(False)
        return super().on_mouse_down(pos)