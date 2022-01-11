import random

import helper
import pygame
import text
from bullet import Bullet
from colors import *
from framesprite import FrameSprite
from particle import Particle
from ships.all_ships import register_ship
from ships.battleship import Battleship
from spritebase import SpriteBase

V2 = pygame.math.Vector2


class WarpWarning(FrameSprite):
    def __init__(self, scene, pos, ship):
        super().__init__(pos, "assets/warning.png", 19)
        self.scene = scene
        self.ship = ship
        self.wt = 10
        self.text = text.Text(str(10), "small", self.pos + V2(7,6), PICO_ORANGE, shadow=True)
        self.scene.ui_group.add(self.text)
        self._offset = (0.5,0.5)
        self._recalc_rect()

    def update(self, dt):
        self.wt -= dt
        self.text.set_text("%d" % self.wt)
        self.frame = int((self.wt * 4) % 2)
        if self.wt < 0:
            self.kill()
            self.ship.pos = self.pos
            self.ship.is_warping = False
            self.ship.warp_line.kill()
        return super().update(dt)

    def kill(self):
        self.text.kill()
        return super().kill()


class WarpLine(SpriteBase):
    def __init__(self, a, b):
        SpriteBase.__init__(self, a.pos)
        self.obj_a = a
        self.obj_b = b
        self._timers['off'] = 0
        self._generate_image()

    def _generate_image(self):
        delta = self.obj_b.pos - self.obj_a.pos
        w = max(abs(delta.x),1)
        h = max(abs(delta.y),1)
        pt1 = V2(0 if delta.x > 0 else w, 0 if delta.y > 0 else h)
        pt2 = V2(w if delta.x > 0 else 0, h if delta.y > 0 else 0)

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)

        dist = (pt2-pt1).length()
        dn = (pt2-pt1).normalize()
        lp1 = pt1 + (dn * ((self._timers['off'] * 16) % 10 + 5))
        for i in range(int(dist / 10)):
            pygame.draw.line(self.image, PICO_ORANGE, lp1, (lp1 + dn * 3), 1)
            lp1 += dn * 10


        self._width = w
        self._height = h

        self._offset = (0 if delta.x > 0 else 1, 0 if delta.y > 0 else 1)
        self._recalc_rect()

    def update(self, dt):
        self._generate_image()
        self.pos  = V2(self.obj_a.pos)
        return super().update(dt)

@register_ship
class Alien1Battleship(Battleship):
    HEALTHBAR_SIZE = (24,2)
    SHIP_NAME = "alien1battleship"
    SHIP_BONUS_NAME = 'battleship'
    DISPLAY_NAME = "Crusher"

    BASE_HEALTH = 200
    FIRE_RATE = 0.8

    def __init__(self, scene, pos, owning_civ):
        Battleship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-battleship.png", 14)

        self.is_warping = False
        self.warp_target = None
        self.warp_line = None

    def get_max_speed(self):        
        speed = super().get_max_speed()
        if self.is_warping:
            speed *= 0.3
        return speed

    def set_target(self, target):
        super().set_target(target)
        if (target.pos - self.pos).length_squared() > 100 ** 2:
            self.is_warping = True
            delta = target.pos - self.pos
            dn = delta.normalize()
            p = target.pos - dn * (target.radius + 15)
            self.warp_target = WarpWarning(self.scene, p, self)
            self.scene.game_group.add(self.warp_target)
            self.warp_line = WarpLine(self, self.warp_target)
            self.scene.game_group.add(self.warp_line)

    def kill(self):
        if self.warp_target:
            self.warp_target.kill()
        if self.warp_line:
            self.warp_line.kill()
        return super().kill()

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['homing'] = 3
        mods['life'] = 3
        return mods

    def fire(self, at):
        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        for j in range(3):
            towards = (self.effective_target.pos - self.pos).normalize()
            b = Bullet(self.pos, self.effective_target, self, vel=helper.random_angle() * 10, mods=self.prepare_bullet_mods())
            self.scene.game_group.add(b)

            for i in range(3):
                pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalize() * 30 * (random.random() + 0.25)
                p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
                self.scene.add_particle(p)

            enemies = self.scene.get_enemy_objects(self.owning_civ)
            threat_range = self.THREAT_RANGE_DEFAULT
            if self.chosen_target.owning_civ == self.owning_civ: # Target is our own planet (defense)
                threat_range = self.THREAT_RANGE_DEFENSE
            threats = [
                e for e in enemies
                if ((e.pos - self.pos).length_squared() < threat_range ** 2 and e.is_alive())
            ]
            if threats:
                self.effective_target = random.choice(threats)                
