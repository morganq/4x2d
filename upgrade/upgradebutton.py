import pygame
import sound
import text
from colors import *
from economy import RESOURCE_COLORS
from resources import resource_path
from spritebase import SpriteBase

from upgrade import upgradeicon
from upgrade.upgrades import UPGRADE_CATEGORY_COLORS

HOVER_COLORS = {
    PICO_BLUE:PICO_DARKBLUE,
    PICO_LIGHTGRAY:PICO_DARKGRAY,
    PICO_GREEN:PICO_DARKGREEN
}

WHITE_TIME = -0.2
DITHER_WHITE_TIME = -0.06
REVEAL_TIME = 0

class UpgradeButton(SpriteBase):
    def __init__(self, pos, upgrade, onclick, onhoverchange, time = 0):
        super().__init__(pos)
        self.upgrade = upgrade
        self.onclick_callback = onclick
        self.onhoverchange = onhoverchange
        self.selectable = True
        self.time = time
        self.dither_image = pygame.image.load(resource_path("assets/dither_white.png")).convert_alpha()

        self._generate_image()

    def onclick(self):
        sound.play("click1")
        self.onclick_callback()

    def _generate_image(self, hover=False):
        w = 240
        h = 31
        pad = 6
        resource_color = RESOURCE_COLORS[self.upgrade.resource_type]
        upgrade_color = UPGRADE_CATEGORY_COLORS[self.upgrade.category]

        desc_rect = text.render_multiline(self.upgrade.description, "small", PICO_WHITE, 200, False).get_rect()
        h = desc_rect[3] + 19

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        if hover:
            pygame.draw.rect(self.image, PICO_BLACK, (0,0,w,h), 0)
            text_color = PICO_LIGHTGRAY
        else:
            pygame.draw.rect(self.image, PICO_DARKGRAY, (0,0,w,h), 0)
            text_color = PICO_LIGHTGRAY            

        icon = upgradeicon.generate_upgrade_image(self.upgrade)
        self.image.blit(icon, (pad - 2, pad - 3))
        
        text.FONTS["small"].render_to(self.image, (31 + pad, pad - 1), self.upgrade.title, upgrade_color)
        text.render_multiline_to(self.image, (31 + pad, pad + 12), self.upgrade.description, "small", text_color, 200, False)

        
        if self.time < WHITE_TIME:
            pygame.draw.rect(self.image, PICO_BLUE, (0,0,w,h), 0)
            cw = w // 2
            ch = h // 2
            question_mark = text.render_multiline("?", "big", PICO_BLACK)
            self.image.blit(question_mark, (cw - question_mark.get_width() // 2, ch - question_mark.get_height() // 2))
        elif self.time < DITHER_WHITE_TIME:
            pygame.draw.rect(self.image, PICO_WHITE, (0,0,w,h), 0)
        elif self.time < REVEAL_TIME:
            self.image.blit(self.dither_image, (0,0))

        self._width = w
        self._height = h
        self._recalc_rect()    

    def update(self, dt):
        self.time += dt
        if self.time < REVEAL_TIME + 1:
            self._generate_image()
        return super().update(dt)

    def on_mouse_enter(self, pos):
        self._generate_image(True)
        self.onhoverchange(True, self)
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self._generate_image(False)
        self.onhoverchange(False, self)
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        self.onclick()
        return super().on_mouse_down(pos)        
