from meter import Meter
from v2 import V2
from colors import *
from particle import Particle
from explosion import Explosion
import random

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

        self._shield_damage = 0
        self.shield_bar = Meter(V2(self.x, self.y - self._height / 2 - 3), meter_size[0], 2, PICO_BLUE, 1)
        self.shield_bar.value = 9999999
        self.shield_bar.offset = (0.5,1)
        self.shield_bar.stay = False
        self.shield_bar.visible = 0
        self.shield_bar._recalc_rect()
        scene.ui_group.add(self.shield_bar)        

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
            if old > 0 and self._health <= 0:
                self.on_die()

    def on_die(self):
        pass

    def on_health_changed(self, old, new):
        pass

    def get_max_health(self):
        return 1

    def get_max_shield(self):
        return 0

    @property
    def shield(self):
        return max(self.get_max_shield() - self._shield_damage, 0)

    @shield.setter
    def shield(self, value):
        old = self._shield_damage
        self._shield_damage = min(max(self.get_max_shield() - value, 0), self.get_max_shield())
        if old != self._shield_damage:
            self.shield_bar.value = self.shield
            self.shield_bar.max_value = self.get_max_shield()
            self.shield_bar.show()
            self.health_bar.show()

    def take_damage(self, damage, origin=None):
        was_shield = False
        sa = min(damage, self.shield)
        if self.shield > 0:
            was_shield = True
        self.shield -= sa
        damage -= sa
        self.health -= damage
        if origin:
            delta = origin.pos - self.pos
            dn = delta.normalized()
            hitpos = self.pos + dn * self.radius
            if was_shield:
                for i in range(10):
                    ang = dn.to_polar()[1]
                    rad = max(self.radius, 5) + 2
                    hp = self.pos + rad * V2.from_angle(ang + random.random() - 0.5)
                    p = Particle([PICO_GREEN, PICO_WHITE, PICO_BLUE, PICO_BLUE, PICO_BLUE, PICO_BLUE, PICO_DARKBLUE], 1, hp, 0.65 + random.random() * 0.2, dn)
                    self.scene.game_group.add(p)
            else:
                particles = 10
                if self.radius > 6:
                    particles = 4
                    e = Explosion(hitpos, [PICO_WHITE, PICO_YELLOW, PICO_RED], 0.2, 5, "log", 2)
                    self.scene.game_group.add(e)
                for i in range(particles):
                    p = Particle([PICO_WHITE, PICO_YELLOW, PICO_YELLOW, PICO_RED, PICO_LIGHTGRAY], 1, hitpos, 0.25, V2.random_angle() * 9)                
                    self.scene.game_group.add(p)