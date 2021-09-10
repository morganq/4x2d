import math
import time
from os import close

import pygame

import game
import spritebase
from colors import *
from helper import clamp, get_nearest
from v2 import V2

OUTLINE_COLOR = PICO_DARKGRAY
DOT_COLOR = PICO_YELLOW

class FleetDiagram(spritebase.SpriteBase):
    def __init__(self, pos, scene):
        super().__init__(pos)
        self.scene = scene
        self.layer = -2
        self.time = 0
        self.refresh_time = 0

        # debug
        self.debug_times = []
        self.mean_debug_time = 0
        self.max_debug_time = 0

    def update(self, dt):
        self.time += dt
        self.refresh_time -= dt
        if self.refresh_time < 0:
            self.refresh_time = 0
            self.generate_image(self.scene)
            self.debug_times = self.debug_times[-100:]
            if self.debug_times:
                self.mean_debug_time = sum(self.debug_times) / max(len(self.debug_times),1)
                self.max_debug_time = max(self.debug_times)
        return super().update(dt)

    def generate_image(self, scene):
        t1 = time.time()
        self.image = pygame.Surface(game.Game.inst.game_resolution.tuple_int(), pygame.SRCALPHA)
        self._width, self._height = self.image.get_size()

        jump_dist = 3

        fleets = scene.fleet_managers['my'].current_fleets[::]
        fleets.extend(scene.fleet_managers['enemy'].current_fleets[::])
        for fleet in fleets:
            if not fleet.target:
                continue
            if fleet.mode_state() == 'waiting':
                pygame.draw.circle(self.image, OUTLINE_COLOR, fleet.target.pos.tuple(), fleet.target.radius + 15, 3)
                continue       
            #if fleet.mode_state == 'dogfighting':
            #    continue
            center = fleet.pos

            if len(fleet.path) > 1:
                pygame.draw.lines(self.image, OUTLINE_COLOR, False, [p.tuple_int() for p in fleet.path], 3)

            for step in fleet.path:
                self.image.set_at(step.tuple_int(), DOT_COLOR)
        

        self._recalc_rect()
        t2 = time.time()
        self.debug_times.append((t2-t1))
