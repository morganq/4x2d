from colors import PICO_BLACK, PICO_DARKBLUE, PICO_PURPLE
from spritebase import SpriteBase
import pygame

STAY_TIME = 5.0

class Meter(SpriteBase):
    def __init__(self, pos, width, height, color, max_value):
        SpriteBase.__init__(self, pos)
        self.stay = False
        self.stay_time = 0

        self.meter_width = width
        self.meter_height = height
        self.color = color
        self.max_value = max_value

        self._value = 0
        self._apparent_value = 0
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
        if self.meter_height <= 2:
            px = round((self.meter_width - 2) * (self._apparent_value / self.max_value))
            pygame.draw.rect(self.image, PICO_PURPLE, (1,self.meter_height - 1, self.meter_width-2, 1), 0)
            pygame.draw.rect(self.image, self.color, (1,self.meter_height - 1, px, 1), 0)
            pygame.draw.line(self.image, self.color, (0,0), (0,self.meter_height))
            pygame.draw.line(self.image, self.color, (self.meter_width-1,0), (self.meter_width-1,self.meter_height))            
        elif self.meter_height <= 4:
            px = round((self.meter_width - 2) * (self._apparent_value / self.max_value))
            pygame.draw.rect(self.image, PICO_PURPLE, (1,1, self.meter_width-2, self.meter_height-2), 0)
            pygame.draw.rect(self.image, self.color, (1,1, px, self.meter_height - 2), 0)
            pygame.draw.line(self.image, self.color, (0,0), (0,self.meter_height))
            pygame.draw.line(self.image, self.color, (self.meter_width-1,0), (self.meter_width-1,self.meter_height))
        else:
            px = round((self.meter_width - 4) * (self._apparent_value / self.max_value))
            pygame.draw.rect(self.image, self.color, (0,0, self.meter_width, self.meter_height), 1)
            pygame.draw.rect(self.image, self.color, (2,2, px, self.meter_height - 4), 0)

        self._width = self.meter_width
        self._height = self.meter_height
        self._recalc_rect()

    def update(self, dt):
        if self._apparent_value < self._value:
            self._apparent_value = min(self._apparent_value + self.max_value * dt * 2, self._value)
            self._generate_image()
        elif self._apparent_value > self._value:
            self._apparent_value = self._value
            self._generate_image()

        self.stay_time -= dt
        if self.stay_time <= 0 and not self.stay:
            self.visible = 0
        return super().update(dt)