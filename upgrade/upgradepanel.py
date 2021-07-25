import random

import economy
import game
import pygame
from button import Button
from colors import *
from framesprite import FrameSprite
from panel import Panel
from pygame import font
from spritebase import SpriteBase
from text import FONTS, Text
from v2 import V2

from upgrade import upgrades
from upgrade.upgradebutton import UpgradeButton
from upgrade.upgradeicon import UpgradeIcon


class UpgradePanel(Panel):
    def __init__(self, pos, offered_upgrades, resource, on_select, on_reroll):
        Panel.__init__(self, pos, None)
        self.resource = resource
        self.padding = 15
        self.tab = {"text":"Asset: %s" % self.resource.title(), "color":economy.RESOURCE_COLORS[self.resource], "icon":"assets/i-upgrade.png"}
        self.tree_children = []

        self.add(Text("Pick Your Asset", "big", V2(0,0), multiline_width=250), V2(0,0))
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
            if uname:
                b = add_button(uname)
                y += 20 + b.height
            else:
                y += 20

        box = SpriteBase(V2(0,0))
        box._width = 75
        box.visible = False
        self.add(box, V2(250,0))

        self.joystick_controls = []
        self.joystick_controls.extend([[c] for c in self.get_controls_of_type(UpgradeButton)])

        if game.Game.inst.run_info.rerolls > 0:# or game.DEV:
            self.add(Button(V2(0,0), "%d left" % game.Game.inst.run_info.rerolls, "small", on_reroll, icon="assets/die.png", label="REROLL"), V2(0, y + 10))
            self.joystick_controls.append([self.get_control_of_type(Button)])            

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(game.RES[0] / 2 - self._width / 2, game.RES[1] / 2 - self._height / 2)
        self._reposition_children()

    def hover_update(self, hovering, button):
        if hovering == False: return

        self.joystick_controls = [[c] for c in self.get_controls_of_type(UpgradeButton)]
        reroll = self.get_control_of_type(Button)
        if reroll:
            self.joystick_controls.append([reroll])

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
                for u in same_fam[::]:
                    if not u.family['parents'] and not cur_parents:
                        rows[-1].append(u)
                        same_fam.remove(u)
                    elif u.family['parents'] and set(u.family['parents']).issubset(set(cur_parents)):
                        rows[-1].append(u)
                        same_fam.remove(u)
                cur_parents = [u.name for u in rows[-1]]
                
            positions = {}
            for rx, row in enumerate(rows):
                row.sort(key=lambda x:x.name)
                for cy,upg in enumerate(row):
                    pos = V2(self.width - 55, 0)
                    if len(row) > 1:
                        pos = V2(self.width - 75 + cy * 37, 0)
                    icon = UpgradeIcon(pos + V2(self.x - 4, self.y + 50 + rx * 50), upg.name, None, True)
                    self.joystick_controls[rx].append(icon)
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
                    pygame.draw.line(self.image, color, (pos + V2(14, 12) - self.pos).tuple(), (pp + V2(14,12) - self.pos).tuple(), 1)
                if name == button.upgrade.name:
                    pygame.draw.rect(self.image, PICO_GREEN, (pos.x - self.pos.x - 1, pos.y - self.pos.y, 28, 28), 2)
                if u.infinite:
                    inf = FrameSprite(pos + V2(22,23), "assets/infinite.png", 8)
                    if u.name in game.Game.inst.scene.my_civ.researched_upgrade_names:
                        inf.frame = 1
                    else:
                        inf.frame = 0
                    game.Game.inst.scene.ui_group.add(inf)
                    self.tree_children.append(inf)
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

        pygame.draw.rect(self.image, PICO_GREYPURPLE, (self.width - 85, 32, 78, 160))
        FONTS['tiny'].render_to(self.image, (self.width - 83, 24), "TECHNOLOGY TREE", PICO_WHITE)

    def kill(self):
        for child in self.tree_children:
            child.kill()
        self.tree_children = []
        return super().kill()
