import random

import helper
import pygame
from bullet import Bullet
from colors import *
from helper import get_nearest
from particle import Particle
from ships.all_ships import register_ship
from ships.bomber import Bomber
from ships.fighter import Fighter
from ships.ship import THRUST_PARTICLE_RATE, Ship


@register_ship
class Alien3Bomber(Fighter):
    SHIP_NAME = "alien3bomber"    
    DISPLAY_NAME = "Void Bomber"
    BOMB_DAMAGE = 25
    BASE_DAMAGE = 12
    FIRE_RANGE = 35
    BASE_HEALTH = 35
    FIRE_RATE = 0.33

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3bomber.png", 13)   

    def near_enemies(self):
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_ships(self.scene.player_civ))
        if dsq < 30 ** 2:
            return True
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_planets(self.scene.player_civ))
        if dsq < 50 ** 2:
            return True            
        return False

    def prepare_bomb_mods(self):
        mods = self.prepare_bullet_mods()
        mods['color'] = PICO_RED
        mods['shape'] = 'circle'
        mods['size'] = 1
        mods['missile_speed'] = -0.3
        mods['trail'] = PICO_RED
        mods['damage_base'] = self.BOMB_DAMAGE
        return mods        

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['color'] = PICO_RED
        return mods

    def fire_bomb(self, at):
        towards = helper.try_normalize(at.pos - self.pos)
        self.last_shot_at = at

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(self.pos, at, self, mods=self.prepare_bomb_mods())
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = helper.try_normalize(towards + pygame.math.Vector2(random.random() * 0.75, random.random() * 0.75)) * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)       

    def fire(self, at):
        if isinstance(at, Ship):
            return super().fire(at)    
        else:
            return self.fire_bomb(at)

    def update(self, dt):
        if self.in_void() and not self.near_enemies():
            self.visible = False
        else:
            self.visible = True
        return super().update(dt)

    def emit_thrust_particles(self):
        if self.in_void():
            return
        return super().emit_thrust_particles()
