from re import M

from colors import *
from economy import RESOURCE_COLORS, RESOURCES
from line import Line
from panel import Panel
from piechart import PieChart
from simplesprite import SimpleSprite
from text import Text
from upgrade.upgradeicon import UpgradeIcon
from v2 import V2


class PlanetPanel(Panel):
    def __init__(self, planet):
        Panel.__init__(self, (5,5), planet)
        self.planet = planet
        
        owner = "Neutral"
        color = PICO_YELLOW
        is_mine = False
        if planet.owning_civ:
            color = planet.owning_civ.color
            if planet.owning_civ.is_enemy:
                owner = "Enemy"
            else:
                owner = "Your"
                is_mine = True

        self.tab = {'text':'%s Planet' % (owner,), 'color':color, 'icon':'assets/i-planet.png'}
        self.add(Text("Health: %d/%d" % (planet.health, planet.get_max_health()), "small", (0,0), PICO_WHITE, False, multiline_width=120), V2(0,0))
        self.add(Text("Resources", "small", (0,0), PICO_WHITE, False), V2(0,15))
        
        y = 30
        chart_data = {}
        for r in RESOURCES:
            pr = getattr(planet.resources, r)
            if pr:
                self.add(SimpleSprite((0,0), 'assets/i-%s.png' % r), V2(0,y))
                self.add(Text(r.title(), "small", (0,0), PICO_WHITE, False), V2(15,y+2))
                self.add(Text("%s%%" % pr, "small", (0,0), PICO_WHITE, False), V2(40,y+2))
                y += 15
                chart_data[RESOURCE_COLORS[r]] = pr
      
        self.add(PieChart((0,0), chart_data), V2(70, 10))

        y = max(y + 7, 41)
        self.add(Line(V2(0,0), V2(96, 0), PICO_WHITE),V2(0, y))
        y += 5

        self.add(SimpleSprite((0,0), 'assets/i-pop.png'), V2(34,y))
        color = PICO_WHITE
        if planet.population == 0 or planet.population >= planet.get_max_pop():
            color = PICO_YELLOW
        if planet.owning_civ == None or is_mine or planet.in_comm_range:
            self.add(Text("%d/%d" %(planet.population, planet.get_max_pop()), "small", (0,0), color, False), V2(47,y+1))
        else:
            self.add(Text("?/%d" %planet.get_max_pop(), "small", (0,0), color, False), V2(47,y+1))

        y += 14
        if sum(planet.ships.values()) and (is_mine or planet.in_comm_range):
            self.add(Line(V2(0,0), V2(96, 0), PICO_WHITE),V2(0, y))
            y += 4
            ships_alpha = sorted(planet.ships.keys())
            maxxed = False
            if sum(planet.ships.values()) > planet.get_max_ships():
                maxxed = True
            for ship in ships_alpha:
                if planet.ships[ship] <= 0:
                    continue
                try:
                    self.add(SimpleSprite((0,0), 'assets/i-%s.png' % ship), V2(0,y))
                except:
                    print("ERROR FINDING ICON FOR %s" % ship)
                    pass
                self.add(Text("%ss" % ship.title(), "small", (0,0), PICO_WHITE, False), V2(15,y + 2))
                color = PICO_WHITE
                if maxxed:
                    color = PICO_RED
                self.add(Text("%d" % planet.ships[ship], "small", (0,0), color, False), V2(88,y + 2))
                y += 15

        if planet.buildings and is_mine:
            
            self.add(Line(V2(0,0), V2(96, 0), PICO_WHITE),V2(0, y))
            y += 5
            for i, building in enumerate(planet.buildings):
                x = (i % 3) * 33
                if (i % 3) == 0 and i > 0: y += 27
                s = UpgradeIcon(V2(0,0),building['building'].upgrade.name,None,True)
                self.add(s, V2(x + 3,y))

            y += 14

        self.redraw()
