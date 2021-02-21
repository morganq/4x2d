from meter import Meter
from v2 import V2
from colors import *

class Healthy:
    def __init__(self, scene):
        self._health = self.get_max_health()
        self.health_bar = Meter(V2(self.x - 15, self.y - self._height / 2 - 2), 30, 6, PICO_RED, self.get_max_health())
        self.health_bar.value = self.health
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
            self.health_bar.show()

    def get_max_health(self):
        return 0