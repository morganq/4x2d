from meter import Meter
from v2 import V2
from colors import *

class Healthy:
    def __init__(self, scene, meter_size = (30,4)):
        self._health = 1
        self.health_bar = Meter(V2(self.x, self.y - self._height / 2), meter_size[0], meter_size[1], PICO_RED, 1)
        self.health_bar.value = self.health
        self.health_bar.offset = (0.5,1)
        self.health_bar.stay = False
        self.health_bar.visible = 0
        self.health_bar._recalc_rect()
        scene.ui_group.add(self.health_bar)

    def set_health(self, health, show_healthbar=False):
        self.health = health
        self.health_bar.visible = show_healthbar

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
            self.on_health_changed(old, self._health)

    def on_health_changed(self, old, new):
        pass

    def get_max_health(self):
        return 1