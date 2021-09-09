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
            self.refresh_time = 0.1
            #self.generate_image(self.scene)
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
            path = []
            ship = fleet.ships[0]
            if not ship.chosen_target:
                continue
            if fleet.mode_state() == 'waiting':
                pygame.draw.circle(self.image, OUTLINE_COLOR, ship.chosen_target.pos.tuple(), ship.chosen_target.radius + 15, 3)
                continue       
            if fleet.mode_state == 'dogfighting':
                continue
            center = fleet.get_size_info()[0]
            p_end = ship.chosen_target.pos
            p_current = ship.starting_pos
            if (center - p_end).sqr_magnitude() < 30 ** 2:
                path = [center, p_end]
            else:
                iterations = 0
                while (p_current - p_end).sqr_magnitude() > (jump_dist + ship.chosen_target.radius + 3) ** 2:
                    if scene.flowfield.has_field(ship.chosen_target):
                        p_current = scene.flowfield.walk_field(p_current, ship.chosen_target, jump_dist)
                    else:
                        break
                    
                    path.append(p_current)
                    iterations += 1
                    if iterations > 1000:
                        print("fleet diagram way too many iterations! giving up")
                        break

            if path:
                closest_dist, closest = min([((p - (center + ship.velocity.normalized() * jump_dist * 2)).sqr_magnitude(), p) for p in path])
                last_point = None
                past_fleet = False
                for i,point in enumerate(path):
                    if point == closest:
                        past_fleet = True
                    if last_point and past_fleet:
                        size = 3
                        pygame.draw.line(self.image, OUTLINE_COLOR, last_point.tuple_int(), point.tuple_int(), size)
                    last_point = point

                past_fleet = False
                ci = int((self.time * 2) % 2)
                for i,point in enumerate(path):
                    if point == closest:
                        past_fleet = True
                    if past_fleet:
                        color = PICO_BLACK
                        if i % 2 == ci:
                            self.image.set_at(point.tuple_int(), DOT_COLOR)
                    
        self._recalc_rect()
        t2 = time.time()
        self.debug_times.append((t2-t1))
