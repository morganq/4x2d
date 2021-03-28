from status_effect import GreyGooEffect
from colors import *
from v2 import V2
from spritebase import SpriteBase
import pygame
import math
import helper
import random

VEL = 50
DEATH_TIME = 5
DAMAGE = 2

class Bullet(SpriteBase):
    def __init__(self, pos, target, shooter, vel=None, mods=None):
        SpriteBase.__init__(self, pos)
        self.target = target
        self.shooter = shooter
        self.owning_civ = self.shooter.owning_civ
        self.collidable = True
        self.collision_radius = 2
        self.mods = mods or {}
        speed = VEL * (1 + self.mods.get("ship_missile_speed", 0))
        if vel:
            self.vel = vel.normalized() * speed
        else:
            self.vel = (self.get_target_pos() - self.pos).normalized() * speed
        self.offset = (0.5, 0.5)
        self.time = 0
        self._generate_image()

    def collide(self, other):
        if other.owning_civ == self.shooter.owning_civ: return
        if not getattr(other, "health", None): return
        if other.get_stat("ship_dodge") > 0:
            if random.random() <= other.get_stat("ship_dodge"):
                print("dodge")
                self.kill()
                return
                
        damage = self.mods.get("damage_base", 1)
        damage *= 1 + self.mods.get("damage_mul", 0)
        damage += self.mods.get("damage_add", 0)
        objs_hit = [other]
        if self.mods.get("blast_radius", False):
            objs_hit = helper.all_nearby(self.pos, self.shooter.scene.get_enemy_objects(self.owning_civ), self.mods.get("blast_radius"))
            
        for obj in objs_hit:
            obj.health -= damage
            if self.mods.get("grey_goo", False):
                obj.add_effect(GreyGooEffect(other, self))
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
        pygame.draw.line(self.image, self.mods.get("color", PICO_BLUE), p1.tuple(), p2.tuple(), 1)

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