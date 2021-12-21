import pygame
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

class UpgradeButton(SpriteBase):
    def __init__(self, pos, upgrade, onclick, onhoverchange):
        super().__init__(pos)
        self.upgrade = upgrade
        self.onclick = onclick
        self.onhoverchange = onhoverchange
        self.selectable = True

        self._generate_image()

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

        self._width = w
        self._height = h
        self._recalc_rect()    

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
