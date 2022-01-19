import pygame

impor helper

import text
from colors import PICO_WHITE
from helper import clamp
from spritebase import SpriteBase

V2 = pygame.math.Vector2


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

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.line(self.image, self.color, pt1, pt2, 1)
        self._width = w
        self._height = h

        self._offset = (0 if delta.x > 0 else 1, 0 if delta.y > 0 else 1)
        self._recalc_rect()

class AssetLine(Line):
    def __init__(self, start, end, color):
        super().__init__(start, end, color)
        self.next_line = None
        self.time = -999999999
        self.pt_start  = V2(self.pt1)
        self.pt_final  = V2(self.pt2)
        self.delta = helper.try_normalize(self.pt2 - self.pt1)
        self.len = (self.pt2 - self.pt1).length()
        self.pt2  = V2(self.pt1)
        self.visible = False
        self._generate_image()
    
    def start(self):
        self.time = 0
        self.visible = True
        self.update_len()

    def update_len(self):
        t = self.time * 1750
        l1 = clamp(t, 0, self.len)
        self.pt2 = self.pt_start + self.delta * l1
        l2 = clamp(t - 800, 0, self.len)
        self.pt1 = self.pt_start + self.delta * l2
        if l1 >= self.len:
            if self.next_line and self.next_line.time < 0:
                self.next_line.start()
        if l2 >= self.len:
            self.kill()
        self._generate_image()
        self.pos = self.pt1

    def update(self, dt):
        self.time += dt
        self.update_len()
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
