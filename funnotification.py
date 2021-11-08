import random

import game
from colors import *
from helper import clamp
from text import Text
from v2 import V2

COLORS = [PICO_BLUE, PICO_WHITE, PICO_PINK, PICO_YELLOW, PICO_GREEN]

class FunNotification(Text):
    def __init__(self, text, target=None):
        self.color_index = 0
        size = "big"
        if target:
            size="small"
        super().__init__(text.upper(), size, V2(0,0), color=COLORS[0], border=False, multiline_width=game.RES[0], shadow=PICO_BLACK)
        self.pos = V2(game.RES[0] / 2, game.RES[1] / 2)
        if target:
            if isinstance(target, V2):
                self.pos = V2(
                    clamp(target.x, self.width/2, game.RES[0] - self.width/2),
                    clamp(target.y, self.height/2, game.RES[1] - self.height/2)
                )
            else:                
                self.pos = V2(
                    clamp(target.pos.x, self.width/2, game.RES[0] - self.width/2),
                    clamp(target.pos.y, self.height/2, game.RES[1] - self.height/2)
                )
        self.offset = (0.5, 0.5)
        self._recalc_rect()
        

    def update(self, dt):
        self.color_index += dt
        self.color = COLORS[int(self.color_index * 12) % len(COLORS)]
        self.pos = V2(self.pos.x, self.pos.y - 10 / (self.color_index+0.5) * dt)
        self.update_image()
        if self.color_index >= 2.5:
            self.kill()
        