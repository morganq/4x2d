import pygame

import text
from colors import PICO_WHITE
from spritebase import SpriteBase
from v2 import V2


def ptmin(a,b):
    if a.x > b.x:
        return b
    return a

def ptmax(a,b):
    if a.x > b.x:
        return a
    return b

class Line(SpriteBase):
    def __init__(self, start, end, color):
        self.pt1 = ptmin(start, end)
        self.pt2 = ptmax(start, end)
        self.color = color
        SpriteBase.__init__(self, self.pt1)
        self._generate_image()

    def _generate_image(self):
        delta = self.pt2 - self.pt1
        w = max(abs(delta.x),1)
        h = max(abs(delta.y),1)
        pt1 = V2(0 if delta.x > 0 else abs(delta.x), 0 if delta.y > 0 else abs(delta.y))
        pt2 = V2(abs(delta.x) if delta.x > 0 else 0, abs(delta.y) if delta.y > 0 else 0)
        print (delta, w,h,pt1,pt2)

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.line(self.image, self.color, pt1.tuple(), pt2.tuple(), 1)
        self._width = w
        self._height = h

        self._offset = (0 if delta.x > 0 else 1, 0 if delta.y > 0 else 1)
        self._recalc_rect()

class AssetLine(Line):
    def __init__(self, start, end, color):
        super().__init__(start, end, color)
        self.time = 0
    
    def update(self, dt):
        self.time += dt
        if self.time < 0.75:
            if (self.time * 8) % 1 > 0.5:
                self.visible = False
            else:
                self.visible = True
        else:
            self.visible = True
        if self.time > 1.5:
            self.kill()
        return super().update(dt)

class IndicatorLine(Line):
    def __init__(self, planet, start, end, color, name=None):
        self.planet = planet
        self.name = name
        self.name_text = None
        self.time = 0
        super().__init__(start, end, color)
        if self.name:
            self.name_text = text.Text(self.name, "tiny", (start + end) / 2, multiline_width=80, shadow=True)
            self.name_text.offset = (0.5,0.5)
            self.planet.scene.ui_group.add(self.name_text)

    def update(self, dt):
        self.time += dt
        if self.time < 1:
            if (self.time * 6) % 1 < 0.5:
                self.visible = False
            else:
                self.visible = True
        else:
            if self.planet.frame == 1:
                self.visible = True
                self.name_text.visible = True
            else:
                self.visible = False
                self.name_text.visible = False
        return super().update(dt)

    def kill(self):
        if self.name_text:
            self.name_text.kill()
        return super().kill()
