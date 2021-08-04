import game
import rewardscene
from button import Button
from colors import *
from economy import RESOURCE_COLORS, RESOURCES
from line import Line
from panel import Panel
from piechart import PieChart
from pygame import Rect
from rectangle import Rectangle
from simplesprite import SimpleSprite
from text import Text
from upgrade.upgradeicon import UpgradeIcon
from v2 import V2


class GalaxyPanel(Panel):
    def __init__(self, galaxy, onclick, onsignal=None):
        Panel.__init__(self, V2(5,5), galaxy)
        self.padding = 3 # ??
        self.galaxy = galaxy
        
        self.tab = {'text':"Sector %d" % galaxy.coords[0], 'color':(0,0,0,0)}

        if self.galaxy.signal:
            w = 165
        else:
            w = 145

        self.add(Line(V2(0,0), V2(w,0), PICO_RED), (V2(0,0)))
        self.add(Rectangle(V2(0,0), (w - 63, 16), PICO_RED), V2(63,0))
        self.add(SimpleSprite(V2(0,0), "assets/panel-enemy.png"), V2(7,5))
        
        self.add(Text("Alien Sector", "small", (0,0), PICO_WHITE, False, multiline_width=100), V2((w-63) / 2 + 34,3)) 
        if self.galaxy.signal == "future_tech":
            self.add(Text("Enemy: Unknown", "small", (0,0), PICO_WHITE, False, multiline_width=100), V2(65,23)) 
            self.add(Text("Has Future Tech!", "small", (0,0), PICO_YELLOW, False, multiline_width=100), V2(65,35)) 
        else:
            self.add(Text("Enemy: Unknown", "small", (0,0), PICO_WHITE, False, multiline_width=100), V2(65,28)) 

        self.add(Line(V2(0,0), V2(w,0), PICO_RED), (V2(0,52)))
        self.add(Line(V2(0,0), V2(w,0), PICO_RED), (V2(0,54)))

        self.add(Text("Victory Reward", "tiny", (0,0), PICO_GREYPURPLE, False, multiline_width=200), V2(w/2 - 30,62)) 
        rh = 28
        self.add(Rectangle(V2(0,0), (w, rh), PICO_GREYPURPLE), V2(0,77))
        reward_icon = SimpleSprite(V2(0,0), "assets/%s.png" % galaxy.rewards[0])
        reward_name = rewardscene.REWARDS[galaxy.rewards[0]]['title']
        reward_name = "\n".join([line for line in reward_name.split(" ")])
        reward_text = Text(reward_name, "small", (0,0), PICO_WHITE, False, multiline_width=140, center=False)
        reward_width = reward_text.width + 6 + reward_icon.width
        self.add(reward_icon, V2(w / 2 - reward_width / 2, 91 - reward_icon.height / 2))
        self.add(reward_text, V2(w / 2 - reward_width / 2 + reward_icon.width + 6, 91 - reward_text.height / 2 + 2))

        if galaxy.playable or game.DEV:
            lt = "LAUNCH >"
            st = "DECODE ?"
            if game.Game.inst.input_mode == "joystick":
                lt = "[*x*] LAUNCH >"
                st = "[*square*] DECODE ?"
            self.launch_button = Button(V2(0,0), lt, 'small', lambda:onclick(galaxy), color=PICO_PINK)
            self.signal_button = None
            if self.galaxy.signal:
                self.add(self.launch_button, V2(w - self.launch_button.width - 5, 121))
                self.signal_button = Button(V2(0,0), st, 'small', lambda:onsignal(galaxy), color=PICO_BLUE)
                self.add(self.signal_button, V2(5, 121))                
            else:
                self.add(self.launch_button, V2(w / 2 - self.launch_button.width / 2, 121))

            self.add(Line(V2(0,0), V2(w,0), PICO_DARKBLUE), (V2(0,146)))

        self.redraw()

    def position_nicely(self, scene):
        y = self.panel_for.y - self._height / 2
        x = self.panel_for.apparent_pos.x + self.panel_for._width / 2 + 10
        offset = 0
        if x > game.RES[0] / 2:
            offset = -self.width * 1.5 + 0
        
        self.pos = V2(self.panel_for.x + self.panel_for._width / 2 + 10 + offset,y)
        self._reposition_children()

    def press_confirm(self):
        self.launch_button.onclick()

    def press_signal(self):
        if self.signal_button:
            self.signal_button.onclick()
