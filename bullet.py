import math
import random

import pygame

import helper
import planet
import satellite
import ships
import sound
from colors import *
from explosion import Explosion
from planet import building
from spritebase import SpriteBase
from status_effect import GreyGooEffect
from v2 import V2

VEL = 50
DEATH_TIME = 1
DAMAGE = 2
NEAR_ENEMY_PLANETS_DIST = 60

class Bullet(SpriteBase):
    def __init__(self, pos, target, shooter, vel=None, mods=None):
        SpriteBase.__init__(self, pos)
        self.target = target
        self.shooter = shooter
        self.owning_civ = self.shooter.owning_civ
        self.collidable = True
        self.stationary = False
        self.collision_radius = 5
        self.mods = mods or {}
        speed = VEL * (1 + self.mods.get("missile_speed", 0))
        if vel:
            self.vel = vel.normalized() * speed
        else:
            self.vel = (self.get_target_pos() - self.pos).normalized() * speed

        self.death_time = self.mods.get("life", None) or DEATH_TIME
        self.offset = (0.5, 0.5)
        self.time = 0
        self._generate_image()

        # mod vars
        self.bounces = self.mods.get("bounces", 0)

    def collide(self, other):
        if other.owning_civ == self.shooter.owning_civ: return
        if not getattr(other, "health", None): return
        reflect = False
        if isinstance(other, satellite.ReflectorShieldObj):
            if not other.bullet_hits(self):
                return
            else:
                reflect = True
        if isinstance(other, building.ReflectorShieldCircleObj):
            if not other.bullet_hits(self):
                return
            else:
                reflect = True

        if not reflect:
            if self.target and self.target != other: return # No accidentally hitting stuff.

        if other.get_stat("ship_dodge") > 0:
            if random.random() <= other.get_stat("ship_dodge"):
                self.kill()
                return

        if other.get_stat("ship_dodge_near_enemy_planets"):
            nearest, dist = helper.get_nearest(other.pos, other.scene.get_enemy_planets(other.owning_civ))
            if dist < NEAR_ENEMY_PLANETS_DIST ** 2:     
                if random.random() <= other.get_stat("ship_dodge_near_enemy_planets"):
                    self.kill()                       

        if isinstance(other, ships.bomber.Bomber):
            if other.get_dodges_left() > 0:
                other.dodge()
                self.kill()
                return
                
        damage = self.mods.get("damage_base", 1)
        damage *= 1 + self.mods.get("damage_mul", 0)
        damage += self.mods.get("damage_add", 0)
        objs_hit = [other]
        if self.mods.get("blast_radius", False):
            objs_hit.extend(helper.all_nearby(self.pos, self.shooter.scene.get_enemy_objects(self.owning_civ), self.mods.get("blast_radius")))
            color = self.mods.get("color", PICO_BLUE)
            e = Explosion(self.pos, [PICO_WHITE, color, DARKEN_COLOR.get(color, PICO_DARKGRAY)], 0.25, self.mods.get("blast_radius"), "log", line_width=1)
            self.shooter.scene.game_group.add(e)
            sound.play("aoe")
            
        for obj in objs_hit:
            pre_health = obj.health
            obj.take_damage(damage, self)
            post_health = obj.health

            if isinstance(obj, planet.planet.Planet):
                if pre_health > 0 and post_health <= 0:
                    if self.mods.get("raze_upgrade"):                    
                        civ = self.shooter.owning_civ
                        if civ:
                            r = obj.get_primary_resource()
                            civ.earn_resource(r, civ.upgrade_limits.data[r], obj)

            if self.mods.get("iron_on_hit"):
                if isinstance(obj, ships.ship.Ship):
                    if self.shooter.owning_civ:
                        self.shooter.owning_civ.earn_resource("iron", self.mods.get("iron_on_hit"), where=self.pos)
            if self.mods.get("grey_goo", False):
                obj.add_effect(GreyGooEffect(other, self))
            if self.mods.get("raze_chance", 0):
                if isinstance(obj, planet.planet.Planet):
                    if random.random() < self.mods.get("raze_chance"):
                        obj.raze_building()


        if self.bounces > 0:
            self.bounces -= 1
            targets = self.shooter.scene.get_enemy_objects(self.owning_civ)
            nearby_targets = helper.all_nearby(self.pos, targets, 25)
            if self.target and self.target in nearby_targets:
                nearby_targets.remove(self.target)
            if nearby_targets:
                self.target = random.choice(nearby_targets)
                self.vel = (self.target.pos - self.pos).normalized() * self.vel.magnitude()
            else:
                self.kill()

        else:
            if reflect:
                self.target, self.shooter = self.shooter, self.target
                self.vel = (self.get_target_pos() - self.pos).normalized() * self.vel.magnitude()
                self._generate_image()
            else:
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
        homing_amt = self.mods.get("homing") + self.time / 2
        try:
            ao = math.acos(facing.dot(towards))
        except ValueError:
            ao = 0
        if ao < 0.25 * homing_amt:
            angle = math.atan2(towards.y, towards.x)
        else:
            if cp > 0:
                angle += 3 * dt * homing_amt
            else:
                angle -= 3 * dt * homing_amt
        self.vel = V2.from_angle(angle) * speed
        self._generate_image()

    def update(self, dt):
        self.pos += self.vel * dt
        if self.mods.get("homing", False) and self.target.health > 0:
            self.homing(dt)
        self.time += dt
        if self.time > self.death_time:
            self.kill()
