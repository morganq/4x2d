import random

import economy
import game
import pygame
from button import Button
from colors import *
from framesprite import FrameSprite
from panel import Panel
from pygame import font
from rectangle import Rectangle
from resources import resource_path
from spritebase import SpriteBase
from text import FONTS, Text

V2 = pygame.math.Vector2

from upgrade import upgrades
from upgrade.upgradebutton import UpgradeButton
from upgrade.upgradeicon import UpgradeIcon


class UpgradePanel(Panel):
    def __init__(self, pos, offered_upgrades, resource, on_select, on_reroll, is_new_roll = False):
        Panel.__init__(self, pos, None)
        self.resource = resource
        self.padding = 15
        self.tab = {"text":"Upgrade: %s" % self.resource.title(), "color":economy.RESOURCE_COLORS[self.resource], "icon":"assets/i-upgrade.png"}
        self.tree_children = []

        self.iron_border = pygame.image.load(resource_path("assets/upgrade-border-iron.png")).convert_alpha()
        self.ice_border = pygame.image.load(resource_path("assets/upgrade-border-ice.png")).convert_alpha()
        self.gas_border = pygame.image.load(resource_path("assets/upgrade-border-gas.png")).convert_alpha()

        self.add(Text("Pick Your Upgrade", "big", V2(0,0), multiline_width=250), V2(0,0))
        self.header_ys = []
        self.header_xs = []

        is_new_roll = is_new_roll

        y = 30
        # need fn for closure
        def add_button(uname, button_id):
            u = upgrades.UPGRADE_CLASSES[uname]
            time = -button_id * 0.3 - 0.75
            if not is_new_roll:
                time = 0
            b = UpgradeButton(V2(0,0), u, lambda:on_select(u), self.hover_update, time=time)
            self.add(b, V2(0,y + 12))
            return b

        cts = {'ships':'Order Ships', 'buildings':'Construct Building', 'tech':'Research Technology'}

        order = ['ships', 'buildings', 'tech']

        for i, category in enumerate(order):
            uname = offered_upgrades[category]
            self.header_ys.append(y + 7)
            t = Text(cts[category], "small", V2(0,0), upgrades.UPGRADE_CATEGORY_COLORS[category], multiline_width=150)
            self.add(t, V2(10,y))


            self.header_xs.append(t.width + 10 + 2)
            if uname:
                b = add_button(uname, i)

                if category in ['buildings', 'tech']:
                    r = Rectangle(V2(0,0), (40, 10), PICO_YELLOW)
                    self.add(r, V2(194, y + 8))
                    t2 = Text("+1 Supply", "tiny", V2(0,0), PICO_BLACK)
                    self.add(t2, V2(196, y + 5))

                y += 25 + b.height
                if i == 0:
                    y += 10
            else:
                y += 20

        box = SpriteBase(V2(0,0))
        box._width = 80
        box.visible = False
        self.add(box, V2(250,0))

        self.joystick_controls = []
        self.joystick_controls.extend([[c] for c in self.get_controls_of_type(UpgradeButton)])

        if game.Game.inst.run_info.rerolls > 0:# or game.DEV:
            self.add(Button(V2(0,0), "%d left" % game.Game.inst.run_info.rerolls, "small", on_reroll, icon="assets/die.png", label="REROLL"), V2(0, y + 10))
            self.joystick_controls.append([self.get_control_of_type(Button)])            

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(game.Game.inst.game_resolution.x / 2 - self._width / 2, game.Game.inst.game_resolution.y / 2 - self._height / 2)
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
            dist_from_right = 59
            for rx, row in enumerate(rows):
                row.sort(key=lambda x:x.name)
                for cy,upg in enumerate(row):
                    pos = V2(self.width - dist_from_right, 0)
                    if len(row) > 1:
                        pos = V2(self.width - dist_from_right - 20 + cy * 37, 0)
                    icon = UpgradeIcon(pos + V2(self.x - 4, self.y + 50 + rx * 50), upg.name, None, True)
                    icon.layer = 11
                    self.joystick_controls[rx].append(icon)
                    game.Game.inst.scene.ui_group.add(icon)
                    self.tree_children.append(icon)
                    positions[upg.name] = icon.pos

            self.redraw()

            for name,pos in positions.items():
                u = upgrades.UPGRADE_CLASSES[name]
                color = PICO_LIGHTGRAY
                if game.Game.inst.scene.player_civ.prereqs_met(name):
                    color = PICO_GREEN
                for parent in u.family['parents']:
                    pp = positions[parent]
                    pygame.draw.line(self.image, color, (pos + V2(14, 12) - self.pos), (pp + V2(14,12) - self.pos), 1)
                if name == button.upgrade.name:
                    pygame.draw.rect(self.image, PICO_GREEN, (pos.x - self.pos.x - 1, pos.y - self.pos.y, 28, 28), 2)
                if u.infinite:
                    inf = FrameSprite(pos + V2(22,23), "assets/infinite.png", 8)
                    inf.layer = 12
                    if u.name in game.Game.inst.scene.player_civ.researched_upgrade_names:
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
        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + y1), (x0 + 7, y0 + y1))
        pygame.draw.line(self.image, PICO_GREEN, (x0, y0 + y1), (x0, y0 + y1 + 5))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + self.header_xs[0], y0 + y1), (x0 + 254 - self.padding, y0 + y1))
        pygame.draw.line(self.image, PICO_GREEN, (x0 + 254 - self.padding, y0 + y1), (x0 + 254 - self.padding, y0 + y1 + 5))

        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + y2), (x0 + 7, y0 + y2))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0, y0 + y2), (x0, y0 + y2+5))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + self.header_xs[1], y0 + y2), (x0 + 254 - self.padding, y0 + y2))
        pygame.draw.line(self.image, PICO_LIGHTGRAY, (x0 + 254 - self.padding, y0 + y2), (x0 + 254 - self.padding, y0 + y2+5))    

        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + y3), (x0 + 7, y0 + y3))
        pygame.draw.line(self.image, PICO_ORANGE, (x0, y0 + y3), (x0, y0 + y3+5))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + self.header_xs[2], y0 + y3), (x0 + 254 - self.padding, y0 + y3))
        pygame.draw.line(self.image, PICO_ORANGE, (x0 + 254 - self.padding, y0 + y3), (x0 + 254 - self.padding, y0 + y3+5))

        pygame.draw.rect(self.image, PICO_GREYPURPLE, (self.width - 90, 32, 78, 160))
        FONTS['tiny'].render_to(self.image, (self.width - 88, 29), "TECHNOLOGY TREE", PICO_WHITE)

        # DEBUG
        resource = self.resource

        if resource == "iron":
            self.image.blit(self.iron_border, (3,17))
            self.image.blit(self.iron_border, (3,self.height - 10))
            pygame.draw.rect(self.image, PICO_LIGHTGRAY, (5, 24, 3, self._height - 34))
            pygame.draw.line(self.image, PICO_DARKGRAY, (6,24), (6, self._height - 34))
            pygame.draw.rect(self.image, PICO_LIGHTGRAY, (self._width - 8, 24, 3, self._height - 34))
            pygame.draw.line(self.image, PICO_DARKGRAY, (self._width - 7,24), (self._width - 7, self._height - 34))

        elif resource == "ice":
            self.image.blit(self.ice_border, (3,17))
            self.image.blit(pygame.transform.flip(self.ice_border, False, True), (3,self._height - 14))

        elif resource == "gas":
            self.image.blit(self.gas_border, (3,17))
            self.image.blit(pygame.transform.flip(self.gas_border, True, True), (3,self._height - 10))
            left = pygame.transform.rotate(self.gas_border, 90)
            ch = self._height - 20
            self.image.blit(left, (3,17), (0,0,7,ch))
            right = pygame.transform.rotate(self.gas_border, -90)
            self.image.blit(right, (self.width - 10,17), (0,0,7,ch))

    def kill(self):
        for child in self.tree_children:
            child.kill()
        self.tree_children = []
        return super().kill()
