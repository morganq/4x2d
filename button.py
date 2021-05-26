import pygame
from colors import *
from spritebase import SpriteBase
import text
from fadeinmixin import FadeInMixin
from resources import resource_path

SIZE_PADDING = {'tiny':4, 'small':7, 'medium':10, 'big':12, 'huge':18}
HEIGHTS = {'tiny':5, 'small':7, 'medium':16, 'big':10, 'huge':15}

class Button(SpriteBase, FadeInMixin):
    def __init__(self, pos, text, size, onclick, image_path=None):
        SpriteBase.__init__(self, pos)
        self.color = PICO_WHITE
        self.text = text
        self.size = size
        self.onclick = onclick
        self.selectable = True
        self.image_path = image_path
        self._generate_image()

    def _generate_image(self, hover=False):
        if self.image_path:
            sheet = pygame.image.load(resource_path(self.image_path)).convert_alpha()
            iw = sheet.get_width() / 2
            self.image = pygame.Surface((iw, sheet.get_height()), pygame.SRCALPHA)
            if hover:
                self.image.blit(sheet, (-iw, 0))
            else:
                self.image.blit(sheet, (0,0))
            self._width, self._height = self.image.get_size()
            self._recalc_rect()
        else:
            self._generate_text_image(hover)

    def _generate_text_image(self, hover=False):
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
        super().on_mouse_down(pos)
        return True