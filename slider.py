import pygame

import text
from colors import *
from spritebase import SpriteBase


class Slider(SpriteBase):
    def __init__(self, pos, meter_width, min, max, onchange=None, value=None, disabled=False, disable_nums=None):
        SpriteBase.__init__(self, pos)
        self.meter_width = meter_width
        self.min = min
        self.max = max
        self.disabled = disabled
        if value is None: self.value = self.min
        else: self.value = value
        self.selectable = True
        self.onchange = onchange
        self.disable_nums = []
        if disable_nums:
            self.disable_nums = disable_nums
        self._generate_image()

    def get_selection_info(self):
        return {'type':'slider'}

    def _generate_image(self):
        pad = 6
        w = self.meter_width + pad * 2
        h = 22

        base_color = PICO_WHITE
        hl_color = PICO_BLUE

        if self.disabled:
            base_color = hl_color = PICO_DARKGRAY

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.line(self.image, base_color, (pad,0), (pad,5), 1)
        pygame.draw.line(self.image, base_color, (w - pad,0), (w - pad,5), 1)
        pygame.draw.line(self.image, base_color, (pad,2), (w-pad,2), 1)
        t = ((self.value - self.min) / self.max - self.min)
        x = int((w-(pad * 2)) * t + pad)
        pts = [(x, 4), (x + 3, 10), (x - 3, 10)]
        if self.value > self.min:
            pygame.draw.rect(self.image, hl_color, (pad + 1,1,x - pad - 1,3), 0)
        pygame.draw.polygon(self.image, base_color, pts,0)

        for i in range(self.max - self.min):
            it = ((i - self.min) / self.max - self.min)
            ix = int((w-(pad * 2)) * it + pad)
            color = base_color
            if (i + self.min) in self.disable_nums:
                color = PICO_DARKGRAY            
            self.image.set_at((ix, 4), color)

        if self.value != self.min:
            mtw = text.FONTS['small'].get_rect(str(self.min))[2]
            text.FONTS['small'].render_to(self.image, (pad - mtw / 2 + 1,13), str(self.min), hl_color)
        if self.value != self.max:
            mtw = text.FONTS['small'].get_rect(str(self.max))[2]
            text.FONTS['small'].render_to(self.image, (w - pad - mtw / 2 + 1,13), str(self.max), hl_color)            

        color = base_color
        if self.value in self.disable_nums:
            color = PICO_DARKGRAY
        tw = text.FONTS['small'].get_rect(str(self.value))[2]
        text.FONTS['small'].render_to(self.image, (x - tw / 2 + 1,13), str(self.value), color)

        self._width = w
        self._height = h
        self._recalc_rect()

    def update_value(self, pos):
        pos = pos - self.pos
        x = (pos.x - 4) / (self.meter_width - 8)
        self.set_value(round(x * (self.max - self.min) + self.min))

    def set_value(self, value):
        if self.disabled: return
        old_value = self.value
        self.value = min(max(value, self.min), self.max)
        if old_value != self.value and self.onchange:
            self.onchange(self.value)
        self._generate_image()        

    def on_mouse_down(self, pos):
        if self.disabled: return
        self.update_value(pos)
        return super().on_mouse_down(pos)

    def on_drag(self, pos):
        if self.disabled: return
        self.update_value(pos)
        return super().on_drag(pos)
