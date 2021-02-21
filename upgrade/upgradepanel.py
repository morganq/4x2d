from button import Button
from panel import Panel
from text import Text
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

        y = 0
        # need fn for closure
        def add_button(uname):
            u = proto.UPGRADE_CLASSES[uname]
            b = Button(V2(0,0),u.title, "small", lambda:on_select(u))
            self.add(b, V2(0,y + 12))

        for category,upgrades in proto.UPGRADES[self.resource].items():
            self.add(Text(category.title(), "small", V2(0,0)), V2(0,y))
            uname = random.choice(upgrades)
            add_button(uname)
            y += 50

        self.redraw()

    def position_nicely(self, scene):
        self.pos = V2(game.RES[0] / 2 - self._width / 2, game.RES[1] / 2 - self._height / 2)
        self._reposition_children()