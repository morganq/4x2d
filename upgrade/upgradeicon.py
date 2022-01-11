import game
import pygame
import text
from colors import *
from economy import RESOURCE_COLORS
from resources import resource_path
from spritebase import SpriteBase
from tooltippanel import TooltipPanel
import pygame
V2 = pygame.math.Vector2

from upgrade.upgrades import UPGRADE_CATEGORY_COLORS, UPGRADE_CLASSES

HOVER_COLORS = {
    PICO_BLUE:PICO_DARKBLUE,
    PICO_LIGHTGRAY:PICO_DARKGRAY,
    PICO_GREEN:PICO_DARKGREEN
}

def generate_upgrade_image(upgrade, disabled=False):
    image = pygame.image.load(resource_path("assets/up-back-iron.png")).convert_alpha()
    dither = pygame.image.load(resource_path("assets/dither.png")).convert_alpha()
    try:
        icon = pygame.image.load(resource_path("assets/upgrades/%s.png" % upgrade.icon)).convert_alpha()
    except:
        print("UPGRADE ICON NOT FOUND:", upgrade.icon)

    category_icons = {'buildings':'i-up-building', 'tech':'i-up-tech', 'ships':'i-up-ship'}
    category_icon = pygame.image.load(resource_path("assets/%s.png" % category_icons[upgrade.category])).convert_alpha()
    image.blit(icon, (4,5))
    image.blit(category_icon, (0,0))
    if disabled:
        #disabled_image = pygame.Surface(image.get_size(), pygame.SRCALPHA)
        #disabled_image.fill((0,0,0,128))
        image.blit(dither, (0,0), (0,0,*image.get_size()))
    return image


class UpgradeIcon(SpriteBase):
    def __init__(self, pos, upgrade_name, onclick = None, tooltip = False, tooltip_position="side", disabled=False):
        super().__init__(pos)
        self.upgrade = UPGRADE_CLASSES[upgrade_name]
        self.onclick = onclick
        self.tooltip = tooltip
        self.tooltip_position = tooltip_position
        self._tooltip_panel = None
        self.selectable = True
        self.layer = 1
        self.radius = 13
        self.disabled = disabled

        self._generate_image()

    def _generate_image(self, hover=False):
        self.image = generate_upgrade_image(self.upgrade, disabled=self.disabled)

        self._width = self.image.get_width()
        self._height = self.image.get_height()
        self._recalc_rect()    

    def on_mouse_enter(self, pos):
        self._generate_image(True)
        if self._tooltip_panel:
            self._tooltip_panel.kill()
        if self.tooltip:
            self._tooltip_panel = TooltipPanel(self.upgrade.title, self.upgrade.description)
            if self.tooltip_position == "side":
                if self._tooltip_panel.width + self.pos.x + 30 > game.Game.inst.game_resolution.x:
                    self._tooltip_panel.pos = self.pos + V2(-5 - self._tooltip_panel.width,0)
                else:
                    self._tooltip_panel.pos = self.pos + V2(30,0)
                if self._tooltip_panel.height + self._tooltip_panel.y > game.Game.inst.game_resolution.y:
                    self._tooltip_panel.pos = (self._tooltip_panel.pos.x, game.Game.inst.game_resolution.y - self._tooltip_panel.height)
            elif self.tooltip_position == "bottom":
                x = int(-self._tooltip_panel.width / 2 + self.width / 2)
                self._tooltip_panel.pos = self.pos + V2(x,24)
            self._tooltip_panel._reposition_children()
            self.groups()[0].add(self._tooltip_panel)
            self._tooltip_panel.add_all_to_group(self.groups()[0])
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):       
        self._generate_image(False)
        if self.tooltip and self._tooltip_panel:
            self._tooltip_panel.kill()
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        if self.disabled:
            return        
        if self.onclick:
            self.onclick(self.upgrade)
        if self.tooltip and self._tooltip_panel:
            self._tooltip_panel.kill()
        return super().on_mouse_down(pos)        

    def kill(self):
        if self._tooltip_panel:
            self._tooltip_panel.kill()
        super().kill()
