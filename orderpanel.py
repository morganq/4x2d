from panel import Panel
from slider import Slider
from colors import *
from text import Text
from button import Button
from v2 import V2
from simplesprite import SimpleSprite

class OrderPanel(Panel):
    def __init__(self, pos, planet_from, planet_to, on_order):
        super().__init__(pos, planet_from)
        self.planet_from = planet_from
        self.planet_to = planet_to
        self.on_order = on_order

        self.tab = {'text':"Send Ships", 'color':PICO_RED}

        ships = {**self.planet_from.ships}
        ships['colonist'] = self.planet_from.population

        y = 0
        self.sliders = {}
        for ship in ships.keys():
            if ships[ship]:
                self.add(SimpleSprite((0,0), 'assets/i-%s.png' % ship), V2(0,y))
                self.add(Text("%ss" % ship.title(), "small", (0,0), PICO_WHITE, False), V2(14,y + 2))
                slider = Slider(V2(0,0), 80, 0, ships[ship])
                self.add(slider, V2(0, y+12))
                self.sliders[ship] = slider
                y += 45

        self.add(Button(V2(0,0), "LAUNCH", "small", self.on_launch_click), V2(20, y))

        self.redraw()

    def on_launch_click(self):
        values = {ship:slider.value for ship,slider in self.sliders.items() if slider.value > 0}
        self.on_order(values)