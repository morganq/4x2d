import pygame
from spritebase import SpriteBase
from v2 import V2

def ptmin(a,b):
    if a.x > b.x:
        return b
    return a

def ptmax(a,b):
    if a.x >= b.x:
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
        pt1 = V2(0 if delta.x > 0 else w, 0 if delta.y > 0 else h)
        pt2 = V2(w if delta.x > 0 else 0, h if delta.y > 0 else 0)

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.line(self.image, self.color, pt1.tuple(), pt2.tuple(), 1)
        self._width = w
        self._height = h

        self._offset = (0 if delta.x > 0 else 1, 0 if delta.y > 0 else 1)
        self._recalc_rect()