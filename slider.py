from spritebase import SpriteBase
from colors import *
import pygame
import text

class Slider(SpriteBase):
    def __init__(self, pos, meter_width, min, max):
        SpriteBase.__init__(self, pos)
        self.meter_width = meter_width
        self.min = min
        self.max = max
        self.value = self.min
        self.selectable = True
        self._generate_image()

    def get_selection_info(self):
        return {'type':'slider'}

    def _generate_image(self):
        pad = 6
        w = self.meter_width + pad * 2
        h = 22

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.line(self.image, PICO_WHITE, (pad,0), (pad,5), 1)
        pygame.draw.line(self.image, PICO_WHITE, (w - pad,0), (w - pad,5), 1)
        pygame.draw.line(self.image, PICO_WHITE, (pad,2), (w-pad,2), 1)
        t = ((self.value - self.min) / self.max - self.min)
        x = int((w-(pad * 2)) * t + pad)
        pts = [(x, 4), (x + 3, 10), (x - 3, 10)]
        pygame.draw.polygon(self.image, PICO_WHITE, pts,0)

        tw = text.FONTS['small'].get_rect(str(self.value))[2]
        text.FONTS['small'].render_to(self.image, (x - tw / 2 + 1,13), str(self.value), PICO_WHITE)

        self._width = w
        self._height = h
        self._recalc_rect()

    def update_value(self, pos):
        pos = pos - self.pos
        x = (pos.x - 4) / (self.meter_width - 8)
        self.set_value(round(x * (self.max - self.min) + self.min))

    def set_value(self, value):
        self.value = min(max(value, self.min), self.max)
        self._generate_image()        

    def on_mouse_down(self, pos):
        self.update_value(pos)
        return super().on_mouse_down(pos)

    def on_drag(self, pos):
        self.update_value(pos)
        return super().on_drag(pos)