from button import Button
from colors import *
from panel import Panel
from simplesprite import SimpleSprite
from text import Text
from v2 import V2


class StorePanel(Panel):
    def __init__(self, store_data, pos, panel_for):
        super().__init__(pos, panel_for)
        self.store_data = store_data

        self.tab = {'text':"Shop", 'color':PICO_SKIN}

        self.add(SimpleSprite(V2(0,0), "assets/panel-shop.png"), V2(0,0))
        self.add(Text("Galaxy Shop", "big", V2(0,0), multiline_width=140), V2(70,0))
        self.add(Text("Buy items with credits", "small", V2(0,0), multiline_width=140), V2(85,25))

        self.add(Button(V2(0,0), "Done", "small", None), V2(180,200))

        self.redraw()
