import pygame
from colors import PICO_GREEN
from panel import Panel
from colors import *
from text import Text
from v2 import V2
from simplesprite import SimpleSprite

class HelpPanel(Panel):
    def __init__(self, pos):
        super().__init__(pos, None)
        self.padding = 10
        self.tab = {'text':"Help", 'color':PICO_GREEN}

        y = 0
        def add_text(txt):
            nonlocal y
            t = Text(txt, "small", (0,0), PICO_WHITE, False, 350, center=False)
            self.add(t, V2(26,y))
            y += t.height + 12

        add_text("To order your units around, click and drag from your planet to a target planet. Workers can take control of neutral or heavily damaged planets.")
        add_text("Planets you control generate resources every few seconds based on how many workers are on the planet (population) and which resources are available there. Population also grows over time.")
        add_text("Larger planets have a higher maximum population. Adding workers above that number doesn't help. Click on a planet to see its stats.")
        add_text("Your resources: Iron, Ice, and Gas, accumulate in the meters in the top left. When a resource meter is full, you can UPGRADE!")
        add_text("Each resource provides its own unique upgrades, but upgrades come in three types: BASE CONSTRUCTION, SHIP PRODUCTION, and TECHNOLOGY.")
        add_text("The aliens have started colonizing planets, and will only get more powerful over time. Good luck!")

        self.add(SimpleSprite((0,0), 'assets/help-1.png'), V2(0,0))
        self.add(SimpleSprite((0,0), 'assets/help-2.png'), V2(0,36))
        self.add(SimpleSprite((0,0), 'assets/i-pop.png'), V2(4,95))
        self.add(SimpleSprite((0,0), 'assets/help-3.png'), V2(0,126))
        self.add(SimpleSprite((0,0), 'assets/help-4.png'), V2(0,166))
        self.add(SimpleSprite((0,0), 'assets/help-5.png'), V2(0,206))

        self.redraw()
