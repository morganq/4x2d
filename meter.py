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
        px = round((self.meter_width - 4) * (self._value / self.max_value))
        pygame.draw.rect(self.image, self.color, (0,0, self.meter_width, self.meter_height), 1)
        pygame.draw.rect(self.image, self.color, (2,2, px, self.meter_height - 4), 0)

        self._width = self.meter_width
        self._height = self.meter_height
        self._recalc_rect()

    def update(self, dt):
        self.stay_time -= dt
        if self.stay_time <= 0 and not self.stay:
            self.visible = 0
        return super().update(dt)