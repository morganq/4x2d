import math
import random
from ships.aliencolonist import AlienColonist
from ships.alienfighter import AlienFighter

import framesprite
import pygame
import spritebase
from colors import *
from ships.fighter import Fighter
from ships.colonist import Colonist
from ships.alienbattleship import AlienBattleship
from ships.ship import Ship
from v2 import V2
from meter import Meter
from healthy import Healthy
import economy
import text
from planet.shipcounter import ShipCounter
from icontext import IconText
from collections import defaultdict
from .building import BUILDINGS
from helper import get_nearest
from .planetart import generate_planet_art

EMIT_SHIPS_RATE = 0.125
EMIT_CLASSES = {
    'fighter':Fighter,
    'alien-fighter':AlienFighter,
    'colonist':Colonist,
    'alien-colonist':AlienColonist,
    'alien-battleship':AlienBattleship
}

RESOURCE_BASE_RATE = 1/220.0

POPULATION_GROWTH_TIME = 15
POP_MAX_MUL = 1.0
POP_MAX_ADD = 0
HP_PER_BUILDING = 5
DEFENSE_RANGE = 30
DESTROY_EXCESS_SHIPS_TIME = 7

class Planet(framesprite.FrameSprite, Healthy):
    def __init__(self, scene, pos, size, resources):
        framesprite.FrameSprite.__init__(self, pos, None, 1)
        self.scene = scene
        self.object_type = "planet"
        self.size = size
        self.resources = resources
        self.art = generate_planet_art(self.get_radius(), self.resources.iron, self.resources.ice, self.resources.gas)
        self.resource_timers = economy.Resources(0,0,0)
        self.owning_civ = None
        self.buildings = []
        self.building_slots = [False] * 12
        self.production = []    

        self.base_angle = 0

        self.population = 0
        self.population_growth_timer = 0

        self.upgrade_stats = defaultdict(float)

        self.ships = defaultdict(int)
        self.emit_ships_queue = []
        self.emit_ships_timer = 0

        self.selectable = True
        self.selection_radius = self.size + 14
        self.offset = (0.5, 0.5)
        self._layer = 0
        self.collidable = True
        self.collision_radius = self.size + 8

        self.rotate_rate = random.random() * 0.9 + 1
        self.rotate_timer = random.random() * self.rotate_rate

        self.destroy_excess_ships_timer = 0

        self.needs_panel_update = False

        self._generate_frames()
        self.frame = 0        

        self.shipcounter = ShipCounter(self)
        self.scene.ui_group.add(self.shipcounter)

        Healthy.__init__(self, scene)

    def change_owner(self, civ):
        self.owning_civ = civ
        self.health += self.get_max_health() / 4
        self.population = min(self.population, 1)
        self.buildings = []
        self.ships = defaultdict(int)
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

        # Border
        pygame.draw.circle(frame, color, (cx,cy), radius + border_radius)    

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            building['building'].draw_outline(frame, color, offset, building['angle'] + self.base_angle,expand=border)

        # Foreground
        #pygame.draw.circle(frame, PICO_GREYPURPLE, (cx,cy), radius)
        rotated = pygame.transform.rotate(self.art, 0)
        frame.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            building['building'].draw_foreground(frame, offset, building['angle'] + self.base_angle)

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
        self._recalc_rect()
        self._update_image()

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
        return self.size * 10 + len(self.buildings) * HP_PER_BUILDING

    def get_max_pop(self):
        return self.size * POP_MAX_MUL + POP_MAX_ADD

    def update(self, dt):
        # Spawn ships
        if self.emit_ships_queue:
            self.emit_ships_timer += dt
            if self.emit_ships_timer >= EMIT_SHIPS_RATE:
                ship_type, data = self.emit_ships_queue.pop(0)
                target = data['to']
                ship_class = EMIT_CLASSES[ship_type]
                off = V2(random.random() - 0.5, random.random() - 0.5).normalized()
                s = ship_class(self.scene, self.pos + off * self.get_radius(), self.owning_civ)
                if ship_type in ["colonist", "alien-colonist"]:
                    s.set_pop(data['num'])
                s.target = target
                s._angle = math.atan2(off.y, off.x)
                self.scene.game_group.add(s)
                self.emit_ships_timer -= EMIT_SHIPS_RATE

        # Resource production
        top_resource = "iron"
        if self.resources.ice > self.resources.iron and self.resources.ice >= self.resources.gas:
            top_resource = "ice"
        elif self.resources.gas > self.resources.iron and self.resources.gas > self.resources.ice:
            top_resource = "gas"
        for r in self.resources.data.keys():
            num_mining_buildings = len([b for b in self.buildings if b['building'].upgrade == "mining_rate"])
            stat_rate = 1
            if top_resource == r:
                stat_rate = num_mining_buildings * 0.15 + 1
            workers = min(self.population, self.size)
            self.resource_timers.data[r] += dt * self.resources.data[r] * RESOURCE_BASE_RATE * workers * stat_rate
            v = (self.resources.data[r] / 10.0)
            if self.resource_timers.data[r] > v:
                self.resource_timers.data[r] -= v
                self.owning_civ.resources.set_resource(r, self.owning_civ.resources.data[r] + v)
                if self.owning_civ == self.scene.my_civ:
                    # Add to score!!
                    self.scene.score += v
                    it = IconText(self.pos, None, "+%d" % v, economy.RESOURCE_COLORS[r])
                    it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
                    self.scene.ui_group.add(it)

        # Ship production
        for prod in self.production:
            prod.update(self, dt)
        self.production = [p for p in self.production if not p.done]

        # Ship destruction
        fighter_name =self.get_ship_name("fighter")
        if self.ships[fighter_name] > self.get_max_fighters():
            self.destroy_excess_ships_timer += dt
            if self.destroy_excess_ships_timer >= DESTROY_EXCESS_SHIPS_TIME:
                self.ships[fighter_name] -= 1
                if self.owning_civ == self.scene.my_civ:
                    it = IconText(self.pos, "assets/i-%s.png" % fighter_name, "-1", PICO_PINK)
                    it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
                    self.scene.ui_group.add(it)          
                self.destroy_excess_ships_timer = 0
                self.needs_panel_update = True      
        else:
            self.destroy_excess_ships_timer = 0

        # Population Growth
        if self.owning_civ:
            if self.population > 0:
                self.population_growth_timer += dt
                max_pop = self.get_max_pop()
                if self.population_growth_timer >= POPULATION_GROWTH_TIME and self.population < max_pop:
                    self.population_growth_timer = 0
                    self.population += 1
                    self.needs_panel_update = True
                    if self.owning_civ == self.scene.my_civ:
                        it = IconText(self.pos, "assets/i-pop.png", "+1", PICO_GREEN)
                        it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
                        self.scene.ui_group.add(it)

        if self.health <= 0:
            self.buildings = []
            self.population = 0

        # Building stuff
        for b in self.buildings:
            b['building'].update(self, dt)

        # Detect enemies
        if self.get_threats():
            for i in range(self.ships[self.get_ship_name("fighter")]):
                self.emit_ship(self.get_ship_name("fighter"), {"to":self})
            for i in range(self.ships['alien-battleship']):
                self.emit_ship('alien-battleship', {"to":self})

    def get_max_fighters(self):
        return self.size * 2

    def get_threats(self):
        enemy_ships = self.scene.get_enemy_ships(self.owning_civ)
        ret = []
        for s in enemy_ships:
            dist = (s.pos - self.pos).sqr_magnitude()
            if dist < (self.get_radius() + DEFENSE_RANGE) ** 2:        
                ret.append(s)
        return ret

    def get_ship_name(self, type):
        if self.owning_civ == self.scene.enemy.civ:
            return "alien-" + type
        return type

    def get_workers(self):
        return min(self.population, self.size)

    def emit_ship(self, type, data):
        if type in ['colonist', 'alien-colonist']:
            self.emit_ships_queue.append((type, data))
            self.population -= data['num']
        elif self.ships[type] > 0:
            self.emit_ships_queue.append((type, data))
            self.ships[type] -= 1

    def add_ship(self, type):
        if type in self.ships:
            self.ships[type] += 1
        else:
            self.ships[type] = 1
        if self.owning_civ == self.scene.my_civ:
            it = IconText(self.pos, "assets/i-%s.png" % type, "+1", PICO_PINK)
            it.pos = self.pos - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
            self.scene.ui_group.add(it)      
        self.needs_panel_update = True

    def add_building(self, upgrade):
        mh_before = self.get_max_health()
        angle = 0
        if not all(self.building_slots):
            avail = [i for i,s in enumerate(self.building_slots) if not s]
            choice = random.choice(avail)
            angle = (choice / 12) * 6.2818
            self.building_slots[choice] = True
        else:
            angle = random.random() * 6.2818
        self.buildings.append({"building":BUILDINGS[upgrade](), "angle":angle})
        self._generate_frames()
        self.needs_panel_update = True # Maybe not but w/e
        mh_after = self.get_max_health()
        self._health += mh_after - mh_before 