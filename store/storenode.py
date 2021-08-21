import game
from button import Button
from colors import *
from line import Line
from panel import Panel
from rectangle import Rectangle
from simplesprite import SimpleSprite
from text import Text
from v2 import V2


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
        self.radius = 9

    def get_selection_info(self):
        return {'type':'store'}

class StoreNodePanel(Panel):
    def __init__(self, store, onclick):
        super().__init__(V2(5,5), store)
        self.padding = 3 # ??
        self.store = store
        
        self.tab = {'text':"Sector %d" % store.coords[0], 'color':(0,0,0,0)}

        w = 145

        self.add(Line(V2(0,0), V2(w,0), PICO_SKIN), (V2(0,0)))
        self.add(Rectangle(V2(0,0), (82, 16), PICO_SKIN), V2(w - 82,0))
        self.add(SimpleSprite(V2(0,0), "assets/panel-shop.png"), V2(7,5))
        
        self.add(Text("Shop", "small", (0,0), PICO_BLACK, False, multiline_width=100), V2(94,3)) 
        self.add(Text("Trade Credits\nfor items", "small", (0,0), PICO_WHITE, False, multiline_width=120, center=False), V2(65,25)) 

        self.add(Line(V2(0,0), V2(w,0), PICO_SKIN), (V2(0,52)))
        self.add(Line(V2(0,0), V2(w,0), PICO_SKIN), (V2(0,54)))

        if store.playable or game.DEV:
            t = "VISIT"
            if game.Game.inst.input_mode == "joystick":
                t = "[*x*] VISIT"
            self.button = Button(V2(0,0), t, 'small', lambda:onclick(store), color=PICO_PINK)
            self.add(self.button, V2(36, 70))
            self.add(Line(V2(0,0), V2(w,0), PICO_DARKBLUE), (V2(0,94)))

        self.redraw()

    def position_nicely(self, scene):
        x = self.panel_for.x - self._width / 2
        y = self.panel_for.y - self._height / 2
        x = self.panel_for.x + self.panel_for._width / 2 + 10
        if x > 500:
            x -= self.width * 1.5 + 0
        
        self.pos = V2(x,y)
        self._reposition_children()        

    def press_confirm(self):
        if self.button:
            self.button.onclick()
