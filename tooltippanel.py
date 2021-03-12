from panel import Panel
from colors import *
from text import Text
from v2 import V2

class TooltipPanel(Panel):
    def __init__(self, title, description):
        Panel.__init__(self, (5,5), None)
        t = Text(title, "small", (0,0), PICO_WHITE, False, multiline_width=500)
        t.layer = 3
        self.add(t, V2(0,0))
        t = Text(description, "small", (0,0), PICO_LIGHTGRAY, False, multiline_width=160, center=False)
        t.layer = 3
        self.add(t, V2(0,20))
        self.layer = 2

        self.redraw()