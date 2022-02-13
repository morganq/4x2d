import random

import helper
import laserparticle
import pygame
import sound
from bullet import Bullet
from colors import *
from particle import Particle
from ships.all_ships import register_ship
from ships.fighter import Fighter

V2 = pygame.math.Vector2


@register_ship
class BossLaser(Fighter):
    SHIP_NAME = "bosslaser"
    BASE_HEALTH = 45
    BASE_DAMAGE = 3.0
    FIRE_RATE = 0.25
    FIRE_RANGE = 55
    MAX_SPEED = 4
    FUEL = 9999
    DISPLAY_NAME = "Predator"

    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/bosslaser.png", 13)
        self.fast_fire_timer = 0
        self.bullets_chambered = 0
        self.firing_target = None
        self.fire_timer = 0.75

    def special_fire(self, at):
        towards = helper.try_normalize(at.pos - self.pos)

        b = Bullet(at.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        l = laserparticle.LaserParticle(self.pos, at.pos, self.owning_civ.color, 0.2)
        self.scene.add_particle(l)

        self.bullets_chambered -= 1

    def fire(self, at):
        #sound.play(random.choice(['laser1', 'laser2', 'laser3']))
        self.bullets_chambered = 12
        self.firing_target = at
        self.fast_fire_timer = 0
        self.special_fire(at)

    def update(self, dt):
        if self.bullets_chambered > 0:
            self.target_heading = (self.firing_target.pos - self.pos).as_polar()[1] * 3.14159 / 180
            self.fast_fire_timer += dt
            if self.fast_fire_timer >= 0.2:
                self.fast_fire_timer -= 0.2
                self.special_fire(self.firing_target)
                if self.bullets_chambered <= 0:
                    self.target_heading = None
        return super().update(dt)
        
