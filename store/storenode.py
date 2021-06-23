from v2 import V2
from panel import Panel
from simplesprite import SimpleSprite
import game
from button import Button
from colors import *
from text import Text

class StoreNodeGraphic(SimpleSprite):
    def __init__(self, pos, offerings, coords, playable):
        super().__init__(pos, img="assets/shop.png")
        self.selectable = True
        self.offerings = offerings
        self.coords = coords
        self.selection_radius = self._width // 2 + 4
        self.playable = playable
        self.needs_panel_update = False
        self.offset = (0.5, 0.5)

    def get_selection_info(self):
        return {'type':'store'}

class StoreNodePanel(Panel):
    def __init__(self, store, onclick):
        super().__init__(V2(5,5), store)
        
        self.tab = {'text':"Sector %d" % store.coords[0], 'color':PICO_PINK}

        self.add(Text("Shop", "small", (0,0), PICO_WHITE, False, multiline_width=100), V2(0,0))

        if store.playable or game.DEV:
            self.add(Button(V2(0,0), 'LAUNCH', 'small', lambda:onclick(store), icon="assets/i-colonist.png", color=PICO_PINK), V2(0, 15))

        self.redraw()

    def position_nicely(self, scene):
        x = self.panel_for.x - self._width / 2
        y = self.panel_for.y - self._height / 2
        x = self.panel_for.x + self.panel_for._width / 2 + 10
        if x > 500:
            x -= self.width * 1.5 + 0
        
        self.pos = V2(x,y)
        self._reposition_children()        