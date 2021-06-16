import pygame
from colors import *
from spritebase import SpriteBase
import text
from fadeinmixin import FadeInMixin
from resources import resource_path

SIZE_PADDING = {'tiny':3, 'small':4, 'medium':5, 'big':7, 'huge':10}
HEIGHTS = {'tiny':5, 'small':7, 'medium':16, 'big':10, 'huge':15}

class Button(SpriteBase, FadeInMixin):
    def __init__(self, pos, text, size, onclick, image_path=None, label=None, icon=None, color=PICO_BLUE):
        SpriteBase.__init__(self, pos)
        self.color = color
        self.text = text
        self.size = size
        self.onclick = onclick
        self.selectable = True
        self.image_path = image_path
        self.label = label
        self.icon = icon
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
        w = tw[2] + pad * 4
        h = HEIGHTS[self.size] + pad * 2
        text_offset = 0
        y_offset = 0
        icon = None
        if self.label:
            h += 10
            y_offset = 10

        if self.icon:
            icon = pygame.image.load(resource_path(self.icon)).convert_alpha()
            w += icon.get_width() + 4
            text_offset = icon.get_width() / 2
            if icon.get_height() > HEIGHTS[self.size]:
                h += int((icon.get_height() - HEIGHTS[self.size]))
                y_offset += int((icon.get_height() - HEIGHTS[self.size]) / 2)

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        color = self.color
        text_color = PICO_WHITE
        if hover:
            color = PICO_WHITE
            text_color = PICO_BLACK
        pygame.draw.rect(self.image, color, (0,0,w,h), 0)
        
        text_x = w / 2 - tw[2] / 2 + text_offset
        icon_x = text_x

        text.FONTS[self.size].render_to(self.image, (text_x, pad + y_offset), self.text, text_color)
        if icon:
            icon_x = text_x - 4 - icon.get_width()
            icon_y = pad + y_offset + int((HEIGHTS[self.size] - icon.get_height()) / 2)
            pygame.draw.rect(self.image, PICO_BLACK, (icon_x - 1, icon_y, icon.get_width() + 2, icon.get_height()))
            pygame.draw.rect(self.image, PICO_BLACK, (icon_x, icon_y - 1, icon.get_width(), icon.get_height() + 2))
            self.image.blit(icon, (icon_x, icon_y))

        if self.label:
            text.FONTS['tiny'].render_to(self.image, (icon_x, pad), self.label, text_color)

        z = {'tiny':2, 'small':3,'medium':3,'big':4,'huge':5}[self.size]
        pygame.draw.polygon(self.image, (255,255,255,0), [(w-z,0), (w,0), (w,z)])

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