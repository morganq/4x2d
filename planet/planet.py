import math
import random

import framesprite
import pygame
import spritebase
from colors import *
from ships.fighter import Fighter
from ships.colonist import Colonist
from ships.ship import Ship
from v2 import V2
from meter import Meter
from healthy import Healthy
import economy
from icontext import IconText
from collections import defaultdict

EMIT_SHIPS_RATE = 0.125
EMIT_CLASSES = {
    'fighter':Fighter,
    'colonist':Colonist
}

class Planet(framesprite.FrameSprite, Healthy):
    def __init__(self, scene, pos, size, resources):
        framesprite.FrameSprite.__init__(self, pos, None, 1)
        self.scene = scene
        self.object_type = "planet"
        self.size = size
        self.resources = resources
        self.resource_timers = economy.Resources(0,0,0)
        self.owning_civ = None
        self.buildings = []
        self.population = 0
        self.planet_upgrades = []
        self.production = []

        self.upgrade_stats = defaultdict(float)

        self.ships = {}
        self.emit_ships_queue = []
        self.emit_ships_timer = 0

        self.selectable = True
        self.selection_radius = self.size + 14
        self.offset = (0.5, 0.5)
        self._generate_frames()
        self._layer = 0
        self.collidable = True
        self.collision_radius = self.size + 8

        Healthy.__init__(self, scene)

    def change_owner(self, civ):
        self.owning_civ = civ
        self.health += self.get_max_health() / 4
        self._generate_frames()

    def _generate_frame(self, border = False):
        radius = self.size + 8
        padding = 8
        cx,cy = radius + padding, radius + padding
        self._width = radius * 2 + padding * 2
        self._height = radius * 2 + padding * 2
        frame = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        border_radius = 2 if border else 1
        color = self.owning_civ.color if self.owning_civ else PICO_YELLOW

        pygame.draw.circle(frame, color, (cx,cy), radius + border_radius)    
        pygame.draw.circle(frame, PICO_GREYPURPLE, (cx,cy), radius)
        return frame

    def _generate_frames(self):
        inactive = self._generate_frame(False)
        hover = self._generate_frame(True)
        w = inactive.get_width()
        h = inactive.get_height()
        self._sheet = pygame.Surface((w * 2, h), pygame.SRCALPHA)
        self._sheet.blit(inactive, (0,0))
        self._sheet.blit(hover, (w,0))
        self._width = w
        self._height = h
        self._frame_width = w
        self.frame = 0
        self._recalc_rect()

    def on_mouse_enter(self, pos):
        self.frame = 1
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self.frame = 0
        return super().on_mouse_exit(pos)

    def get_selection_info(self):
        return {"type":"planet","planet":self}

    def get_radius(self):
        return self.size + 8

    def get_max_health(self):
        return self.size * 10 + len(self.buildings) * 5

    def add_building(self, building_type):
        mh_before = self.get_max_health()
        self.buildings.append(building_type)
        mh_after = self.get_max_health()
        self._health += mh_after - mh_before

    def update(self, dt):
        # Spawn ships
        if self.emit_ships_queue:
            self.emit_ships_timer += dt
            if self.emit_ships_timer >= EMIT_SHIPS_RATE:
                ship_type, data = self.emit_ships_queue.pop(0)
                target = data['to']
                #if target is not alive, turn around and go home
                ship_class = EMIT_CLASSES[ship_type]
                off = V2(random.random() - 0.5, random.random() - 0.5).normalized()
                s = ship_class(self.scene, self.pos + off * self.get_radius(), self.owning_civ)
                if ship_type == "colonist":
                    s.population = data['num']
                s.target = target
                s._angle = math.atan2(off.y, off.x)
                self.scene.game_group.add(s)
                self.emit_ships_timer -= EMIT_SHIPS_RATE

        for r in self.resources.data.keys():
            stat_rate = (self.upgrade_stats['mining_rate'] + 1)
            self.resource_timers.data[r] += dt * self.resources.data[r] / 100 * self.population * stat_rate
            v = (self.resources.data[r] / 10)
            if self.resource_timers.data[r] > v:
                self.resource_timers.data[r] -= v
                self.owning_civ.resources.set_resource(r, self.owning_civ.resources.data[r] + v)
                it = IconText(self.pos, None, "+%d" % v, economy.RESOURCE_COLORS[r])
                it.pos = self.pos - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 10
                self.scene.ui_group.add(it)

        for prod in self.production:
            prod.update(self, dt)
        self.production = [p for p in self.production if not p.done]

    def get_workers(self):
        return min(self.population, self.size)

    def add_ship(self, type):
        if type in self.ships:
            self.ships[type] += 1
        else:
            self.ships[type] = 1
