import pygame

import sound
import text
from colors import *
from fadeinmixin import FadeInMixin
from resources import resource_path
from spritebase import SpriteBase
from v2 import V2

SIZE_PADDING = {'tiny':3, 'small':4, 'medium':5, 'big':7, 'huge':10}
HEIGHTS = {'tiny':5, 'small':10, 'medium':16, 'big':10, 'huge':29}

class Button(SpriteBase, FadeInMixin):
    def __init__(self, pos, text, size, onclick, image_path=None, label=None, icon=None, color=PICO_BLUE, asset_border = False, fixed_width = None):
        SpriteBase.__init__(self, pos)
        self.color = color
        self.text = text
        self.size = size
        self.fixed_width = fixed_width
        self.onclick_callback = onclick
        self.selectable = True
        self.image_path = image_path
        self.label = label
        self.icon = icon
        self.joy_button = None
        self.radius = 15
        self.asset_border = asset_border
        self._generate_image()

    def onclick(self):
        sound.play("click1")
        self.onclick_callback()

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
        color = self.color
        text_color = PICO_WHITE
        if sum(color) > 180 * 3:
            text_color = PICO_BLACK
        if hover:
            if self.color == PICO_WHITE:
                color = PICO_LIGHTGRAY
            else:
                color = PICO_WHITE
            text_color = PICO_BLACK        

        text_img = text.render_multiline(self.text, self.size, text_color)
        tw = text_img.get_width()
        
        pad = SIZE_PADDING[self.size]
        w = tw + pad * 4
        h = HEIGHTS[self.size] + pad * 2
        text_offset = 0
        y_offset = 0
        icon = None
        if self.label:
            h += 10
            y_offset = 10

        if self.joy_button:
            text_offset += 16

        if self.icon:
            icon = pygame.image.load(resource_path(self.icon)).convert_alpha()
            w += icon.get_width() + 4
            text_offset += icon.get_width() / 2
            if icon.get_height() > HEIGHTS[self.size]:
                h += int((icon.get_height() - HEIGHTS[self.size]))
                y_offset += int((icon.get_height() - HEIGHTS[self.size]) / 2)

        w = self.fixed_width or w

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0,0,w,h), 0)
        
        text_x = w / 2 - tw / 2 + text_offset
        icon_x = text_x

        #text.FONTS[self.size].render_to(self.image, (text_x, pad + y_offset), self.text, text_color)
        self.image.blit(text_img, (text_x, pad + y_offset))
        if icon:
            icon_x = text_x - 4 - icon.get_width()
            icon_y = pad + y_offset + int((HEIGHTS[self.size] - icon.get_height()) / 2)
            pygame.draw.rect(self.image, PICO_BLACK, (icon_x - 1, icon_y, icon.get_width() + 2, icon.get_height()))
            pygame.draw.rect(self.image, PICO_BLACK, (icon_x, icon_y - 1, icon.get_width(), icon.get_height() + 2))
            self.image.blit(icon, (icon_x, icon_y))

        if self.label:
            #text.render_multiline_to(self.image, (icon_x, pad), self.label, "tiny", text_color)
            text.FONTS['tiny'].render_to(self.image, (icon_x, pad - 4), self.label, text_color)

        z = {'tiny':2, 'small':3,'medium':3,'big':4,'huge':5}[self.size]
        pygame.draw.polygon(self.image, (255,255,255,0), [(w-z,0), (w,0), (w,z)])

        if self.joy_button:
            btn_img = text.render_multiline(self.joy_button, "huge", text_color)
            self.image.blit(btn_img, (4, h // 2 - btn_img.get_height() // 2))

        if self.asset_border:
            pygame.draw.line(self.image, PICO_BLACK, (0,0), (0,h))
            pygame.draw.line(self.image, PICO_BLACK, (0,h-1), (w,h-1))

        self._width = w
        self._height = h
        self._recalc_rect()

    def on_mouse_enter(self, pos):
        if self.onclick:
            self._generate_image(True)
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        if self.onclick:
            self._generate_image(False)
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        if self.onclick:
            self.onclick()
            self._generate_image(True)
            super().on_mouse_down(pos)
            return True
