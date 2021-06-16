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
import game
from button import Button
import rewardscene

DIFFICULTY_NAMES = {
    1:"minor",
    2:"minor",
    3:"major",
    4:"major",
    5:"warning",
    6:"warning",
    7:"do not enter!",
    8:"do not enter!",
    9:"impossible!",
    10:"impossible!",
}

class GalaxyPanel(Panel):
    def __init__(self, galaxy, onclick):
        Panel.__init__(self, (5,5), galaxy)
        self.galaxy = galaxy
        
        self.tab = {'text':"Sector %d" % galaxy.coords[0], 'color':PICO_PINK}
        
        self.add(Text("- THREAT -", "tiny", (0,0), PICO_WHITE, False, multiline_width=100), V2(29,-2)) 
        self.add(Text("UNKNOWN (LEVEL %d)" % (galaxy.difficulty,), "small", (0,0), PICO_WHITE, False, multiline_width=100), V2(0,16))

        self.add(Line(V2(0,0), V2(100,0), PICO_WHITE), (V2(0,30)))

        self.add(Text("- REWARD -", "tiny", (0,0), PICO_WHITE, False, multiline_width=100), V2(29,30)) 
        self.add(SimpleSprite(V2(0,0), "assets/%s.png" % galaxy.rewards[0]), V2(0, 46))
        self.add(Text("[^%s]" % rewardscene.REWARDS[galaxy.rewards[0]]['title'], "small", (0,0), PICO_WHITE, False, multiline_width=100), V2(27,51))
        description = Text(rewardscene.REWARDS[galaxy.rewards[0]]['description'], "small", (0,0), PICO_WHITE, False, multiline_width=110, center=False)
        self.add(description, V2(0,69))

        if galaxy.playable or game.DEV:
            self.add(Button(V2(0,0), 'LAUNCH', 'small', lambda:onclick(galaxy), icon="assets/i-colonist.png", color=PICO_PINK), V2(0, description.height + 72))

        self.redraw()

    def position_nicely(self, scene):
        x = self.panel_for.x - self._width / 2
        y = self.panel_for.y - self._height / 2
        x = self.panel_for.x + self.panel_for._width / 2 + 10
        if x > 500:
            x -= self.width * 1.5 + 0
        
        self.pos = V2(x,y)
        self._reposition_children()