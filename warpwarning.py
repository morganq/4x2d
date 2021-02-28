from framesprite import FrameSprite
from ships.alienbattleship import AlienBattleship
import text
from v2 import V2
from colors import *

WARNINGTIME = 8

class WarpWarning(FrameSprite):
    def __init__(self, planet, scene, pos):
        super().__init__(pos, "assets/warning.png", 19)
        self.planet = planet
        self.scene = scene
        self.wt = WARNINGTIME
        self.text = text.Text(str(WARNINGTIME), "small", self.pos + V2(7,6), PICO_RED)
        self.scene.ui_group.add(self.text)
        self._recalc_rect()

    def update(self, dt):
        self.wt -= dt
        self.text.set_text("%d" % self.wt)
        self.frame = int((self.wt * 4) % 2)
        if self.wt < 0:
            
            self.kill()
            self.text.kill()
            bs = AlienBattleship(self.scene, self.pos, self.scene.enemy.civ)
            bs.target = self.planet
            self.scene.game_group.add(bs)            
        return super().update(dt)