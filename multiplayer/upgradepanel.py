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
from upgrade import upgrades
from upgrade.upgradebutton import UpgradeButton
from upgrade.upgradeicon import UpgradeIcon
from v2 import V2


class UpgradePanel(Panel):
    def __init__(self, pos, civ, offered_upgrades, resource, on_select, on_reroll):
        Panel.__init__(self, pos, None)
        self.civ = civ
        self.resource = resource
        self.tab = {"text":"Upgrade: %s" % self.resource.title(), "color":economy.RESOURCE_COLORS[self.resource], "icon":"assets/i-upgrade.png"}

        y = 0
        # need fn for closure
        def add_button(uname):
            u = upgrades.UPGRADE_CLASSES[uname]
            b = UpgradeIcon(V2(0,0), uname, lambda:on_select(u), True)
            self.add(b, V2(0,y + 12))
            return b

        cts = {'buildings':'Construct Building', 'ships':'Order Ships', 'tech':'Research Technology'}

        for category,uname in offered_upgrades.items():
            b = add_button(uname)
            y += 5 + b.height

        self.joystick_controls = []
        self.joystick_controls.extend([[c] for c in self.get_controls_of_type(UpgradeButton)])

        #if game.Game.inst.run_info.rerolls > 0:
        #    self.add(Button(V2(0,0), "%d left" % game.Game.inst.run_info.rerolls, "small", on_reroll, icon="assets/die.png", label="REROLL"), V2(0, y))
        #    self.joystick_controls.append([self.get_control_of_type(Button)])

        self.redraw()
