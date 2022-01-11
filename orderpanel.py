import asteroid
import game
from button import Button
from colors import *
from panel import Panel
from ships.all_ships import SHIPS_BY_NAME
from simplesprite import SimpleSprite
from slider import Slider
from text import Text
import pygame
V2 = pygame.math.Vector2


class OrderPanel(Panel):
    def __init__(self, pos, planet_from, planet_to, on_order):
        super().__init__(pos, planet_from)
        self.planet_from = planet_from
        self.planet_to = planet_to
        self.on_order = on_order

        siegers_only = isinstance(self.planet_to, asteroid.Asteroid)

        self.tab = {'text':"Send Ships", 'color':PICO_PINK}

        ships = {**self.planet_from.ships}
        ships['colonist'] = self.planet_from.population

        y = 0
        self.sliders = {}
        for ship in ships.keys():
            if ships[ship]:
                if ship == "colonist":
                    name = "Worker"
                else:
                    name = SHIPS_BY_NAME[ship].get_display_name()
                
                color = PICO_WHITE
                disabled = False
                if siegers_only and not SHIPS_BY_NAME[ship].BOMBS:
                    disabled = True                
                    color = PICO_DARKGRAY
                self.add(SimpleSprite((0,0), 'assets/i-%s.png' % ship), V2(0,y))
                self.add(Text("%ss" % name, "small", (0,0), color, False), V2(14,y + 2))
                disable_nums = None
                if self.planet_from.owning_civ.worker_loss > 0:
                    disable_nums = list(range(1, self.planet_from.owning_civ.worker_loss+1))
                slider = Slider(V2(0,0), 80, 0, ships[ship], disabled=disabled, disable_nums=disable_nums)
                self.add(slider, V2(0, y+12))
                self.sliders[ship] = slider
                y += 45

        if not self.sliders:
            self.add(Text("No ships!", "small", V2(0,0)), V2(0,0))
            y += 25

        t = "LAUNCH"
        if game.Game.inst.input_mode == "joystick":
            t = "[*x*] LAUNCH"
        if not self.sliders:
            t = "BACK"
            if game.Game.inst.input_mode == "joystick":
                t = "[*circle*] BACK"
        self.add(Button(V2(0,0), t, "small", self.on_launch_click), V2(20, y))

        self.redraw()

    def on_launch_click(self):
        values = {ship:slider.value for ship,slider in self.sliders.items() if slider.value > 0}
        if 'colonist' in values and values['colonist'] > 0 and values['colonist'] < self.planet_from.owning_civ.worker_loss + 1:
            return
        self.on_order(values)
