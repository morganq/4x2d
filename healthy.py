from meter import Meter
from v2 import V2
from colors import *

class Healthy:
    def __init__(self, scene, meter_size = (30,4)):
        self._health = self.get_max_health()
        self.health_bar = Meter(V2(self.x, self.y - self._height / 2), meter_size[0], meter_size[1], PICO_RED, self.get_max_health())
        self.health_bar.value = self.health
        self.health_bar.offset = (0.5,1)
        self.health_bar.stay = False
        self.health_bar.visible = 0
        self.health_bar._recalc_rect()
        scene.ui_group.add(self.health_bar)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, val):
        old = self._health
        self._health = max(min(val, self.get_max_health()), 0)
        if old != self._health:
            self.health_bar.value = self._health
            self.health_bar.max_value = self.get_max_health()
            self.health_bar.show()

    def get_max_health(self):
        return 0