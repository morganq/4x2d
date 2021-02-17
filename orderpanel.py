from panel import Panel
from slider import Slider
from colors import *
from text import Text
from v2 import V2
from simplesprite import SimpleSprite

class OrderPanel(Panel):
    def __init__(self, pos, planet_from, planet_to):
        super().__init__(pos, planet_from)
        self.planet_from = planet_from
        self.planet_to = planet_to

        self.tab = {'text':"Send Ships", 'color':PICO_RED}

        ships = {**self.planet_from.ships}
        ships['colonist'] = self.planet_from.population

        y = 0
        for ship in ships.keys():
            self.add(SimpleSprite((0,0), 'assets/i-%s.png' % ship), V2(0,y))
            self.add(Text("%ss" % ship.title(), "small", (0,0), PICO_WHITE, False), V2(14,y + 2))
            self.add(Slider(V2(0,0), 80, 0, ships[ship]), V2(0, y+12))
            y += 45

        self.redraw()