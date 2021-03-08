from colors import *
from v2 import V2
from spritebase import SpriteBase
import pygame
import math

VEL = 80
DEATH_TIME = 5

class Bullet(SpriteBase):
    def __init__(self, pos, target, shooter, vel=None, mods=None):
        SpriteBase.__init__(self, pos)
        self.target = target
        self.shooter = shooter
        self.owning_civ = self.shooter.owning_civ
        self.collidable = True
        self.collision_radius = 2
        self.mods = mods or {}
        if vel:
            self.vel = vel
        else:
            self.vel = (self.get_target_pos() - self.pos).normalized() * VEL
        self.offset = (0.5, 0.5)
        self.time = 0
        self._generate_image()

    def collide(self, other):
        if other.owning_civ == self.shooter.owning_civ: return
        if not getattr(other, "health", None): return
        other.health -= 2 * self.mods.get("damage_debuff", 1.0)
        self.kill()

    def get_target_pos(self):
        # Get the target's 'pos' attribute, otherwise assume self.target already *is* a V2
        tp = getattr(self.target, "pos", self.target)
        return tp

    def _generate_image(self):
        self.image = pygame.Surface((9,9), pygame.SRCALPHA)
        vn = self.vel.normalized()
        p1 = V2(4,4)
        p2 = V2(4,4) + vn * 2
        pygame.draw.line(self.image, PICO_BLUE, p1.tuple(), p2.tuple(), 1)

        self._width = 9
        self._height = 9
        self._recalc_rect()

    def homing(self, dt):
        towards = (self.target.pos - self.pos).normalized()
        speed, angle = self.vel.to_polar()
        facing = self.vel.normalized()
        cp = facing.cross(towards)
        try:
            ao = math.acos(facing.dot(towards))
        except ValueError:
            ao = 0
        if ao < 0.25:
            angle = math.atan2(towards.y, towards.x)
        else:
            if cp > 0:
                angle += 3 * dt
            else:
                angle -= 3 * dt
        self.vel = V2.from_angle(angle) * speed
        self._generate_image()

    def update(self, dt):
        self.pos += self.vel * dt
        if self.mods.get("homing", False) and self.target.health > 0:
            self.homing(dt)
        self.time += dt
        if self.time > DEATH_TIME:
            self.kill()