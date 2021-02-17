from spritebase import SpriteBase
import math
from v2 import V2
from colors import *
import pygame

class PieChart(SpriteBase):
    def __init__(self, pos, data):
        SpriteBase.__init__(self, pos)
        self.data = data
        self._generate_image()

    def _generate_image(self):
        r = 13
        color_by_angles = []
        angle_so_far = 0
        for color, value in self.data.items():
            a1 = angle_so_far
            a2 = angle_so_far + value / 100.0 * 6.2818
            color_by_angles.append((a1, a2, color))
            angle_so_far = a2

        self.image = pygame.Surface((r*2,r*2), pygame.SRCALPHA)
        center = V2(r - 0.5,r - 0.5)
        for x in range(r * 2):
            for y in range(r * 2):
                pt = V2(x,y)
                delta = (pt - center)
                if delta.sqr_magnitude() < r**2:
                    angle = math.atan2(delta.y,delta.x) + 3.1415 / 2
                    if angle < 0: angle += 6.2818
                    color = PICO_BLACK
                    for angle1, angle2, anglecolor in color_by_angles:
                        if angle >= angle1 and angle < angle2:
                            color = anglecolor
                    self.image.set_at((pt.x,pt.y), color)

        self._width = self.image.get_width()
        self._height = self.image.get_width()
        self._recalc_rect()