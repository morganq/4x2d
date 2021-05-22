from bullet import Bullet
from colors import PICO_BLUE, PICO_PINK
from spritebase import SpriteBase
import pygame
from spaceobject import SpaceObject
import game
from v2 import V2
import math
import helper

class Satellite(SpaceObject):
    ANGLE_OFFSET = 0
    def __init__(self, scene, planet):
        self.planet = planet
        super().__init__(scene, V2(-50,-50))

    def set_pos(self):
        self.angle = self.scene.time / (self.planet.radius + 10) * 3 + self.ANGLE_OFFSET
        self.angle = self.angle % (math.pi * 2)
        self.pos = self.planet.pos + V2.from_angle(self.angle) * (self.planet.radius + 10)

    def update(self, dt):
        self.set_pos()
        return super().update(dt)


class SpaceStation(Satellite):
    def __init__(self, scene, planet):
        super().__init__(scene, planet)
        self.set_sprite_sheet("assets/spacestation.png", 13)

class ReflectorShieldObj(SpaceObject):
    def __init__(self, scene, sat):
        super().__init__(scene, sat.planet.pos)
        self.sat = sat
        self.collidable = True
        self.stationary = False
        self.radius = sat.planet.radius + 9
        self.collision_radius = self.radius
        self._offset = (0.5, 0.5)
        self._generate_image()
        self.health = 50
        self._timers['regen'] = 0

    def bullet_hits(self, bullet):
        delta = (bullet.pos - self.pos).normalized()
        d, a = delta.to_polar()
        print(a, self.sat.angle)
        if abs(helper.get_angle_delta(a, self.sat.angle)) < math.pi / 2:
            return True
        return False

    def get_max_health(self):
        return 50

    def _generate_image(self):
        r = self.sat.planet.radius + 8
        self._width = r * 2 + 8
        self._height = r * 2 + 8
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        center = V2(r + 4, r + 4)
        pts = 13
        for i in range(pts):
            # angle - quarter circle to angle + quarter circle
            a = self.sat.angle + math.pi / pts * i - math.pi / 2
            p1 = V2.from_angle(a - (math.pi / pts) / 2) * r + center
            p2 = V2.from_angle(a + (math.pi / pts) / 2) * r + center
            pygame.draw.circle(self.image, PICO_PINK, (V2.from_angle(a) * r + center).tuple(), 1.25, 0)
            pygame.draw.line(self.image, PICO_PINK, p1.tuple(), p2.tuple())

        self._recalc_rect()

    def update(self, dt):
        self.health_bar.pos = self.pos + V2(0,-self.sat.planet.radius - 10)
        if self._timers['regen'] > 5:
            self.health += 5
            self._timers['regen'] = 0
        self._generate_image()
        return super().update(dt)
    

class ReflectorShield(Satellite):
    ANGLE_OFFSET = math.pi / 2
    def __init__(self, scene, planet):
        super().__init__(scene, planet)
        self.set_sprite_sheet("assets/reflector.png", 13)
        self.shield_obj = ReflectorShieldObj(scene, self)
        scene.game_group.add(self.shield_obj)

    def kill(self):
        self.shield_obj.kill()
        return super().kill()