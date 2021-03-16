from spritebase import SpriteBase
from button import Button
from panel import Panel
import pygame
from colors import *
from text import Text
from upgrade.upgradebutton import UpgradeButton
import economy
import game
import random
from upgrade import upgrades
from upgrade.upgradeicon import UpgradeIcon
from v2 import V2

class UpgradePanel(Panel):
    def __init__(self, pos, offered_upgrades, resource, on_select):
        Panel.__init__(self, pos, None)
        self.resource = resource
        self.padding = 15
        self.tab = {"text":"Upgrade: %s" % self.resource.title(), "color":economy.RESOURCE_COLORS[self.resource], "icon":"assets/i-upgrade.png"}
        self.tree_children = []

        self.add(Text("Pick Your Upgrade", "big", V2(0,0), multiline_width=250), V2(0,0))
        self.header_ys = []

        y = 30
        # need fn for closure
        def add_button(uname):
            u = upgrades.UPGRADE_CLASSES[uname]
            b = UpgradeButton(V2(0,0), u, lambda:on_select(u), self.hover_update)
            self.add(b, V2(0,y + 12))
            return b

        cts = {'buildings':'Base Construction', 'ships':'Ship Production', 'tech':'Technology'}

        for category,uname in offered_upgrades.items():
            self.header_ys.append(y + 7)
            self.add(Text(cts[category], "small", V2(0,0), upgrades.UPGRADE_CATEGORY_COLORS[category], multiline_width=150), V2(10,y))
            b = add_button(uname)
            y += 20 + b.height

        box = SpriteBase(V2(0,0))
        box._width = 75
        box.visible = False
        self.add(box, V2(250,0))

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(game.RES[0] / 2 - self._width / 2, game.RES[1] / 2 - self._height / 2)
        self._reposition_children()

    def hover_update(self, hovering, button):
        if hovering == False: return

        for child in self.tree_children:
            child.kill()
        self.tree_children = []

        family = button.upgrade.family
        if family:
            same_fam = [uc for uc in upgrades.ALL_UPGRADE_CLASSES if uc.family and uc.family['tree'] == family['tree']]
            same_fam.sort(key=lambda x:x.title)
            cur_parents = []
            rows = []
            for i in range(3):
                rows.append([])
                for u in same_fam:
                    if not u.family['parents'] and not cur_parents:
                        rows[-1].append(u)
                    elif u.family['parents'] and set(u.family['parents']).issubset(set(cur_parents)):
                        rows[-1].append(u)
                cur_parents = [u.name for u in rows[-1]]
                
            positions = {}
            for rx, row in enumerate(rows):
                for cy,upg in enumerate(row):
                    pos = V2(self.width - 55, 0)
                    if len(row) > 1:
                        pos = V2(self.width - 75 + cy * 37, 0)
                    icon = UpgradeIcon(pos + V2(self.x, self.y + 60 + rx * 50), upg.name, None, upg != button.upgrade)
                    if upg == button.upgrade:
                        icon.selectable = False
                    game.Game.inst.scene.ui_group.add(icon)
                    self.tree_children.append(icon)
                    positions[upg.name] = icon.pos

            self.redraw()

            for name,pos in positions.items():
                u = upgrades.UPGRADE_CLASSES[name]
                color = PICO_LIGHTGRAY
                if game.Game.inst.scene.my_civ.prereqs_met(name):
                    color = PICO_GREEN
                for parent in u.family['parents']:
                    pp = positions[parent]
                    pygame.draw.line(self.image, color, (pos + V2(11, 11) - self.pos).tuple(), (pp + V2(11,11) - self.pos).tuple(), 1)
                if name == button.upgrade.name:
                    pygame.draw.rect(self.image, PICO_GREEN, (pos.x - self.pos.x - 1, pos.y - self.pos.y, 28, 28), 2)
        else:
            self.redraw()

    def redraw(self):
        super().redraw()
        x0 = self.padding
        y0 = self.padding + 10
        y1, y2, y3 = self.header_ys
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + y1), (x0 + 7, y0 + y1))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + y1), (x0, y0 + y1 + 5))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + 101, y0 + y1), (x0 + 254 - self.padding, y0 + y1))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + 254 - self.padding, y0 + y1), (x0 + 254 - self.padding, y0 + y1 + 5))

        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + y2), (x0 + 7, y0 + y2))
        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + y2), (x0, y0 + y2+5))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + 87, y0 + y2), (x0 + 254 - self.padding, y0 + y2))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + 254 - self.padding, y0 + y2), (x0 + 254 - self.padding, y0 + y2+5))    

        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + y3), (x0 + 7, y0 + y3))
        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + y3), (x0, y0 + y3+5))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + 68, y0 + y3), (x0 + 254 - self.padding, y0 + y3))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + 254 - self.padding, y0 + y3), (x0 + 254 - self.padding, y0 + y3+5))

        pygame.draw.rect(self.image, PICO_GREYPURPLE, (self.width - 85, 15, 84, self.height - 16))

    def kill(self):
        for child in self.tree_children:
            child.kill()
        self.tree_children = []
        return super().kill()