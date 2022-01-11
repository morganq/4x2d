import random
from collections import defaultdict

import helper
import particle
from animrotsprite import AnimRotSprite
from colors import *
from healthy import Healthy
import pygame
V2 = pygame.math.Vector2


class SpaceObject(AnimRotSprite, Healthy):
    HEALTHBAR_SIZE = (20, 3)
    SOID = 0
    def __init__(self, scene, pos):
        AnimRotSprite.__init__(self, pos)
        self.offset = (0.5, 0.5)
        self.scene = scene
        self.status_effects = []
        self.radius = 1
        self.owning_civ = None
        self.debug_id = self.SOID
        self.stationary = True
        self.solid = True
        self.stealth = False
        SpaceObject.SOID += 1
        Healthy.__init__(self, scene, meter_size=self.HEALTHBAR_SIZE)

    def is_alive(self):
        return self.health > 0 and self.alive()

    def get_stat(self, stat):
        value = 0
        for effect in self.status_effects:
            value += effect.get_stat(stat)
        return value

    def update(self,dt):
        self.update_effects(dt)
        super().update(dt)

    def update_effects(self, dt):
        for effect in self.status_effects:
            effect.update(dt)

    def add_effect(self, effect):
        # Try to stack the effect first of all
        for e in self.status_effects:
            if e.name == effect.name:
                e.stack(effect)
                return

        # Otherwise just add it.
        self.add_single_effect(effect)

    def add_single_effect(self, effect):
        self.status_effects.append(effect)

    def remove_effect(self, effect):
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def remove_all_effects_by_name(self, effect_name):
        self.status_effects = [e for e in self.status_effects if e.name != effect_name]

    def kill(self):
        self.health_bar.kill()
        while(self.status_effects):
            self.status_effects[-1].kill()
        return super().kill()


    def space_explode(self):
        base_angle = random.random() * 6.2818
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                color = tuple(self.image.get_at((x,y)))
                if color[3] >= 128 and color[0:3] != PICO_BLACK:
                    _,a = (V2(x,y) - V2(self.width //2, self.height // 2)).to_polar()
                    if abs(helper.get_angle_delta(a, base_angle)) > 3.14159/2:
                        a = base_angle + 3.14159
                    else:
                        a = base_angle
                    pvel = helper.from_angle(a) * 6
                    p = particle.Particle([PICO_WHITE, PICO_LIGHTGRAY, PICO_DARKGRAY],1,self.pos + V2(x - self.width //2,y - self.height //2),1.5,pvel)
                    self.scene.game_group.add(p)          
