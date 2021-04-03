from piechart import PieChart
from panel import Panel
from text import Text
from simplesprite import SimpleSprite
from upgrade.upgradeicon import UpgradeIcon
from piechart import PieChart
from colors import *
from line import Line
from v2 import V2
from economy import RESOURCES, RESOURCE_COLORS
from button import Button

class GalaxyPanel(Panel):
    def __init__(self, galaxy, onclick):
        Panel.__init__(self, (5,5), galaxy)
        self.galaxy = galaxy
        
        self.add(Text(galaxy.alien.name, "small", (0,0), PICO_WHITE, False), V2(30,5)) 
        self.add(Text(str(galaxy.rewards), "small", (0,0), PICO_WHITE, False), V2(30,17)) 

        if galaxy.playable:
            self.add(Button(V2(0,0), 'LAUNCH', 'small', lambda:onclick(galaxy)), V2(0, 30))

        self.redraw()

    def position_nicely(self, scene):
        x = self.panel_for.x - self._width / 2
        y = self.panel_for.y - self._height / 2
        x = self.panel_for.x + self.panel_for._width / 2 + 10
        
        self.pos = V2(x,y)
        self._reposition_children()