from piechart import PieChart
from panel import Panel
from text import Text
from simplesprite import SimpleSprite
from piechart import PieChart
from colors import *
from line import Line
from v2 import V2
from economy import RESOURCES, RESOURCE_COLORS

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

        self.tab = {'text':'%s Planet' % owner, 'color':color, 'icon':'assets/i-planet.png'}
        self.add(Text("Resources", "small", (0,0), PICO_WHITE, False), V2(0,0))
        
        y = 15
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

        # TODO: center-justify?
        self.add(SimpleSprite((0,0), 'assets/i-pop.png'), V2(34,y))
        self.add(Text("%d/%d" %(planet.population, planet.size), "small", (0,0), PICO_WHITE, False), V2(47,y+1))

        if planet.ships and is_mine:
            y += 14
            self.add(Line(V2(0,0), V2(96, 0), PICO_WHITE),V2(0, y))
            y += 4
            ships_alpha = sorted(planet.ships.keys())
            for ship in ships_alpha:
                self.add(SimpleSprite((0,0), 'assets/i-%s.png' % ship), V2(0,y))
                self.add(Text("%ss" % ship.title(), "small", (0,0), PICO_WHITE, False), V2(15,y + 2))
                self.add(Text("%d" % planet.ships[ship], "small", (0,0), PICO_WHITE, False), V2(88,y + 2))
                y += 15

        self.redraw()