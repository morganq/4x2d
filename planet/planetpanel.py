from re import M

from colors import *
from economy import RESOURCE_COLORS, RESOURCES
from line import Line
from panel import Panel
from piechart import PieChart
from rectangle import Rectangle
from ships.all_ships import SHIPS_BY_NAME
from simplesprite import SimpleSprite
from text import Text
from upgrade.upgradeicon import UpgradeIcon
import pygame
V2 = pygame.math.Vector2


class PlanetPanel(Panel):
    def __init__(self, planet, pov_civ = None):
        Panel.__init__(self, (5,5), planet)
        self.pov_civ = pov_civ
        self.planet = planet
        self.update_planet()
        
    def update_planet(self):
        self.rebuild_panel()
        if self.groups():
            self.add_all_to_group(self.groups()[0])

    def rebuild_panel(self):
        planet = self.planet
        pov_civ = self.pov_civ
        self.empty()
        self.add(Line(V2(0,0), V2(120, 0), PICO_DARKBLUE),V2(0, 0))

        owner = "Neutral"
        color = PICO_YELLOW

        is_mine = False
        if planet.owning_civ:
            color = planet.owning_civ.color
            # If the player's point of view is passed in (multiplayer) then
            # we want the string to be based on if this is that POV civ's planet or not
            if pov_civ is not None:
                if planet.owning_civ != pov_civ:
                    owner = "Enemy"
                else:
                    owner = "Your"
                    is_mine = True
            else:
                if planet.owning_civ.is_enemy:
                    owner = "Enemy"
                else:
                    owner = "Your"
                    is_mine = True


        if not pov_civ:
            pov_civ = self.planet.scene.player_civ # horrible.
        in_comm_range = pov_civ.in_comm_circle(planet.pos)

        self.tab = {'text':'%s Planet' % (owner,), 'color':color, 'icon':'assets/i-planet.png'}
        y = 0

        if is_mine and planet.is_zero_pop():
            t = Text("0 Pop = No Growth!", "small", (0,0), PICO_BLACK, multiline_width=120)
            self.add(Rectangle(V2(0,0), (t.width + 2, 12), PICO_YELLOW), V2(0,y-1))
            self.add(t, V2(1,y + 1))
            y += 17

        if is_mine and planet.has_extra_ships():
            t = Text("Too many ships!", "small", (0,0), PICO_BLACK, multiline_width=120)
            self.add(Rectangle(V2(0,0), (t.width + 2, 12), PICO_YELLOW), V2(0,y-1))
            self.add(t, V2(1,y + 1))
            y += 17

        self.add(Text("Health: %d/%d" % (planet.health, planet.get_max_health()), "small", (0,0), PICO_WHITE, False, multiline_width=120), V2(0,y))
        y += 15
        self.add(Text("Resources", "small", (0,0), PICO_WHITE, False), V2(0,y))
        y += 15        

        chart_y = y - 15
        chart_data = {}
        for r in RESOURCES:
            pr = getattr(planet.resources, r)
            if pr:
                self.add(SimpleSprite((0,0), 'assets/i-%s.png' % r), V2(0,y))
                self.add(Text(r.title(), "small", (0,0), PICO_WHITE, False), V2(15,y+2))
                self.add(Text("%s%%" % pr, "small", (0,0), PICO_WHITE, False), V2(40,y+2))
                y += 15
                chart_data[RESOURCE_COLORS[r]] = pr
      
        self.add(PieChart((0,0), chart_data), V2(80, chart_y - 2))

        y = max(y + 7, 41)
        self.add(Line(V2(0,0), V2(120, 0), PICO_GREYPURPLE),V2(0, y))
        y += 5

        self.add(SimpleSprite((0,0), 'assets/i-pop.png'), V2(44,y))
        color = PICO_WHITE
        if planet.population == 0 or planet.population >= planet.get_max_pop():
            color = PICO_YELLOW
        if planet.owning_civ == None or is_mine or in_comm_range:
            self.add(Text("%d/%d" %(planet.population, planet.get_max_pop()), "small", (0,0), color, False), V2(57,y+1))
        else:
            self.add(Text("?/%d" %planet.get_max_pop(), "small", (0,0), color, False), V2(57,y+1))

        y += 14
        if sum(planet.ships.values()) and (is_mine or in_comm_range):
            self.add(Line(V2(0,0), V2(120, 0), PICO_GREYPURPLE),V2(0, y))
            y += 4
            ships_alpha = sorted(planet.ships.keys())
            maxxed = False
            if sum(planet.ships.values()) > planet.get_max_ships():
                maxxed = True
            for ship in ships_alpha:
                if planet.ships[ship] <= 0:
                    continue
                icon = SimpleSprite((0,0), 'assets/i-%s.png' % ship)
                self.add(icon, V2(0,y))
                iconoffset = 0
                if icon.width < 5:
                    iconoffset = 15
                ship_class = SHIPS_BY_NAME[ship]
                
                self.add(Text("%ss" % ship_class.get_display_name(), "small", (0,0), PICO_WHITE, False, multiline_width=105), V2(15 - iconoffset,y + 2))
                color = PICO_WHITE
                if maxxed:
                    color = PICO_RED
                self.add(Text("%d" % planet.ships[ship], "small", (0,0), color, False), V2(108,y + 2))
                y += 15

        if planet.buildings and is_mine:
            self.add(Line(V2(0,0), V2(120, 0), PICO_GREYPURPLE),V2(0, y))
            y += 5
            for i, building in enumerate(planet.buildings):
                x = (i % 4) * 29
                if (i % 4) == 0 and i > 0: y += 27
                s = UpgradeIcon(V2(0,0),building['building'].upgrade.name,None,True)
                self.add(s, V2(x + 3,y))

            y += 14

        self.redraw()
