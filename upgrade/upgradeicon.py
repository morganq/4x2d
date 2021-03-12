from colors import *
from resources import resource_path
from spritebase import SpriteBase
from tooltippanel import TooltipPanel
from v2 import V2
import pygame
import game
import text
from economy import RESOURCE_COLORS
from upgrade.upgrades import UPGRADE_CATEGORY_COLORS, UPGRADE_CLASSES

HOVER_COLORS = {
    PICO_BLUE:PICO_DARKBLUE,
    PICO_LIGHTGRAY:PICO_DARKGRAY,
    PICO_GREEN:PICO_DARKGREEN
}

class UpgradeIcon(SpriteBase):
    def __init__(self, pos, upgrade_name, onclick = None, tooltip = False):
        super().__init__(pos)
        self.scene = game.Game.inst.scene
        self.upgrade = UPGRADE_CLASSES[upgrade_name]
        self.onclick = onclick
        self.tooltip = tooltip
        self._tooltip_panel = None
        self.selectable = True
        self.layer = 1

        self._generate_image()

    def _generate_image(self, hover=False):
        w = 23
        h = 23
        pad = 0
        resource_color = RESOURCE_COLORS[self.upgrade.resource_type]
        upgrade_color = UPGRADE_CATEGORY_COLORS[self.upgrade.category]

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)       

        pygame.draw.rect(self.image, resource_color, (pad+1,pad,21,23), 0)
        pygame.draw.rect(self.image, resource_color, (pad,pad+1,23,21), 0)
        try:
            icon = pygame.image.load(resource_path("assets/upgrades/%s.png" % self.upgrade.icon)).convert_alpha()
            self.image.blit(icon, (pad + 2, pad + 2))
        except:
            print(self.upgrade.icon)

        self._width = w
        self._height = h
        self._recalc_rect()    

    def on_mouse_enter(self, pos):
        self._generate_image(True)
        if self.tooltip:
            self._tooltip_panel = TooltipPanel(self.upgrade.title, self.upgrade.description)
            if self._tooltip_panel.width + self.pos.x + 30 > game.RES[0]:
                self._tooltip_panel.pos = self.pos + V2(-5 - self._tooltip_panel.width,0)
            else:
                self._tooltip_panel.pos = self.pos + V2(30,0)
            self._tooltip_panel._reposition_children()
            self._tooltip_panel.add_all_to_group(self.scene.ui_group)
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self._generate_image(False)
        if self.tooltip and self._tooltip_panel:
            self._tooltip_panel.kill()
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        if self.onclick:
            self.onclick()
        return super().on_mouse_down(pos)        
