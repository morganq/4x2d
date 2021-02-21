from colors import *
from v2 import V2
from spritebase import SpriteBase
import pygame

VEL = 20
DEATH_TIME = 5

class Bullet(SpriteBase):
    def __init__(self, pos, target, shooter, mods):
        SpriteBase.__init__(self, pos)
        self.target = target
        self.shooter = shooter
        self.owning_civ = self.shooter.owning_civ
        self.collidable = True
        self.collision_radius = 2
        self.vel = (self.get_target_pos() - self.pos).normalized() * VEL
        self.offset = (0.5, 0.5)
        self.time = 0
        self._generate_image()

    def collide(self, other):
        if other.owning_civ == self.shooter.owning_civ: return
        other.health -= 2
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


    def update(self, dt):
        self.pos += self.vel * dt
        self.time += dt
        if self.time > DEATH_TIME:
            self.kill()