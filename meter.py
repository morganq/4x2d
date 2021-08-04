import pygame

from colors import (DARKEN_COLOR, PICO_BLACK, PICO_DARKBLUE, PICO_PURPLE,
                    PICO_YELLOW)
from spritebase import SpriteBase

STAY_TIME = 5.0

class Meter(SpriteBase):
    def __init__(self, pos, width, height, color, max_value):
        SpriteBase.__init__(self, pos)
        self.stay = False
        self.stay_time = 0

        self.flash_time = 0

        self.meter_width = width
        self.meter_height = height
        self.color = color
        self.max_value = max_value

        self._value = 0
        self._apparent_value = 0
        self._generate_image()

    def set_width(self, new_width):
        if new_width != self.width:
            self._width = new_width
            self.meter_width = new_width
            self._generate_image()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, nv):
        self._value = nv
        self._generate_image()

    def show(self):
        self.stay_time = STAY_TIME
        self.visible = 1

    def _generate_image(self):
        self.image = pygame.Surface((self.meter_width, self.meter_height), pygame.SRCALPHA)
        max_value = max(self.max_value, 1)
        if self.meter_height <= 2:
            px = round((self.meter_width - 2) * (self._apparent_value / max_value))
            pygame.draw.rect(self.image, DARKEN_COLOR[self.color], (1,self.meter_height - 1, self.meter_width-2, 1), 0)
            pygame.draw.rect(self.image, self.color, (1,self.meter_height - 1, px, 1), 0)
            pygame.draw.line(self.image, self.color, (0,0), (0,self.meter_height))
            pygame.draw.line(self.image, self.color, (self.meter_width-1,0), (self.meter_width-1,self.meter_height))            
        elif self.meter_height <= 4:
            px = round((self.meter_width - 2) * (self._apparent_value / max_value))
            pygame.draw.rect(self.image, DARKEN_COLOR[self.color], (1,1, self.meter_width-2, self.meter_height-2), 0)
            pygame.draw.rect(self.image, self.color, (1,1, px, self.meter_height - 2), 0)
            pygame.draw.line(self.image, self.color, (0,0), (0,self.meter_height))
            pygame.draw.line(self.image, self.color, (self.meter_width-1,0), (self.meter_width-1,self.meter_height))
        else:
            px = round((self.meter_width - 4) * (self._apparent_value / max_value))
            pygame.draw.rect(self.image, self.color, (0,0, self.meter_width, self.meter_height), 1)
            color = self.color
            if self.flash_time > 0:
                px = (self.meter_width - 4)
                color = self.color if (self.flash_time * 8) % 1 > 0.5 else PICO_YELLOW
            pygame.draw.rect(self.image, color, (2,2, px, self.meter_height - 4), 0)

        self._width = self.meter_width
        self._height = self.meter_height
        self._recalc_rect()

    def flash(self):
        self.flash_time = 2

    def update(self, dt):
        if self.flash_time > 0:
            self.flash_time -= dt
            self._generate_image()
            self.visible = 1
            return

        if self._apparent_value < min(self._value, self.max_value):
            self._apparent_value = min(self._apparent_value + self.max_value * dt * 2, self._value)
            self._generate_image()
        elif self._apparent_value > self._value:
            self._apparent_value = self._value
            self._generate_image()

        self.stay_time -= dt
        if self.stay_time <= 0 and not self.stay and self.visible:
            self.visible = 0
        return super().update(dt)
