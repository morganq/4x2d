from button import Button
from panel import Panel
import pygame
from colors import *
from text import Text
from upgrade.upgradebutton import UpgradeButton
import economy
import game
import random
from upgrade import proto
from v2 import V2

class UpgradePanel(Panel):
    def __init__(self, pos, resource, on_select):
        Panel.__init__(self, pos, None)
        self.resource = resource
        self.padding = 15
        self.tab = {"text":"Upgrade: %s" % self.resource.title(), "color":economy.RESOURCE_COLORS[self.resource], "icon":"assets/i-upgrade.png"}

        self.add(Text("Pick Your Upgrade", "big", V2(0,0), multiline_width=250), V2(0,0))

        y = 30
        # need fn for closure
        def add_button(uname):
            u = proto.UPGRADE_CLASSES[uname]
            b = UpgradeButton(V2(0,0), u, lambda:on_select(u))
            self.add(b, V2(0,y + 12))

        cts = {'buildings':'Base Construction', 'ships':'Ship Production', 'tech':'Technology'}
        for category,upgrades in proto.UPGRADES[self.resource].items():
            self.add(Text(cts[category], "small", V2(0,0), proto.UPGRADE_CATEGORY_COLORS[category], multiline_width=150), V2(10,y))
            uname = random.choice(upgrades)
            add_button(uname)
            y += 60

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(game.RES[0] / 2 - self._width / 2, game.RES[1] / 2 - self._height / 2)
        self._reposition_children()

    def redraw(self):
        super().redraw()
        x0 = self.padding
        y0 = self.padding + 10
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + 37), (x0 + 7, y0 + 37))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + 37), (x0, y0 + 42))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + 101, y0 + 37), (x0 + 254 - self.padding, y0 + 37))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + 254 - self.padding, y0 + 37), (x0 + 254 - self.padding, y0 + 42))

        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + 97), (x0 + 7, y0 + 97))
        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + 97), (x0, y0 + 102))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + 87, y0 + 97), (x0 + 254 - self.padding, y0 + 97))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + 254 - self.padding, y0 + 97), (x0 + 254 - self.padding, y0 + 102))    

        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + 157), (x0 + 7, y0 + 157))
        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + 157), (x0, y0 + 162))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + 68, y0 + 157), (x0 + 254 - self.padding, y0 + 157))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + 254 - self.padding, y0 + 157), (x0 + 254 - self.padding, y0 + 162))                