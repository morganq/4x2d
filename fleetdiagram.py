import math
import time
from os import close

import pygame

import game
import helper
import spritebase
from colors import *
from helper import clamp, get_angle_delta, get_nearest

V2 = pygame.math.Vector2

OUTLINE_COLOR = PICO_LIGHTGRAY
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


    def smooth_path(self, path:list):
        # give up if we don't have enough points to smooth
        if len(path) < 5:
            return path

        smoothed_path = [path[0], path[1]]
        for i in range(2, len(path)-2):
            pt = (path[i-2] + path[i+2]) / 2
            smoothed_path.append(pt)

        smoothed_path.append(path[-2])
        smoothed_path.append(path[-1])
        return smoothed_path

    def generate_image(self, scene):
        t1 = time.time()
        self.image = pygame.Surface(tuple(game.Game.inst.game_resolution), pygame.SRCALPHA)
        #return
        self._width, self._height = self.image.get_size()

        jump_dist = 3

        #fleets = scene.fleet_managers['my'].current_fleets[::]
        #fleets.extend(scene.fleet_managers['enemy'].current_fleets[::])
        fleets = []
        for fleet_manager in scene.fleet_managers.values():
            fleets.extend(fleet_manager.current_fleets[::])
            
        for fleet in fleets:
            if not fleet.target:
                continue
            if fleet.mode_state() == 'waiting':
                pygame.draw.circle(self.image, OUTLINE_COLOR, fleet.target.pos, fleet.target.radius + 15, 3)
                continue       
            if all([s.stealth == True for s in fleet.ships]):
                continue
            #if fleet.mode_state == 'dogfighting':
            #    continue
            center = fleet.pos

            valid_path = fleet.path
            if fleet.last_valid_path:
                valid_path = fleet.last_valid_path
            #path = self.smooth_path(valid_path)
            path = valid_path

            # todo: migrate from center to path.
            original_path = path[::]
            path = path[2:-2]
            if len(path) > 3:
                end_backwards = fleet.target.pos - original_path[int(len(original_path) * 0.75)]
                pygame.draw.circle(self.image, OUTLINE_COLOR, center, 2, 0)
                end_pt = fleet.target.pos - helper.try_normalize(end_backwards) * (fleet.target.radius + 8)

                if (fleet.pos - fleet.target.pos).length_squared() < (fleet.target.radius + 80) ** 2:
                    blended_path = [
                        center,
                        end_pt
                    ]
                    last_delta = helper.try_normalize(end_pt - center)
                else:
                    # Blend the end of the path
                    blended_path = path[::]
                    if (original_path[-1] - fleet.target.pos).length_squared() < (fleet.target.radius + 50) ** 2:
                        blendsteps = min(15, len(blended_path) // 2 - 1)
                        offset = blended_path[-1] - end_pt
                        for i in range(blendsteps):
                            z = (1 - (i / blendsteps))
                            blended_path[-(i+1)] = blended_path[-(i+1)] * (1-z) + end_pt * z
                    
                    # Blend the start of the path
                    blendsteps = min(15, len(blended_path) // 2)
                    offset = blended_path[0] - center
                    for i in range(blendsteps):
                        z = (1 - (i / blendsteps))
                        blended_path[i] = blended_path[i] - offset * z
                    last_delta = (blended_path[-1] - blended_path[-3])
                    if last_delta.x or last_delta.y:
                        last_delta = helper.try_normalize(last_delta)

                pygame.draw.lines(self.image, OUTLINE_COLOR, False, [tuple(p) for p in blended_path], 1)
                
                last_side = V2(last_delta.y, -last_delta.x)
                ap1 = blended_path[-1]
                ap2 = blended_path[-1] + last_delta * -5 + last_side * 5
                ap3 = blended_path[-1] + last_delta * -5 + last_side * -5
                poly = [tuple(ap1), tuple(ap2), tuple(ap3)]
                pygame.draw.polygon(self.image, OUTLINE_COLOR, poly, 0)
        

        self._recalc_rect()
        t2 = time.time()
        self.debug_times.append((t2-t1))
