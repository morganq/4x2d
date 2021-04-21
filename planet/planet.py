import math
import random
from upgrade.upgrades import UPGRADE_CLASSES
from ships.aliencolonist import AlienColonist
from ships.alienfighter import AlienFighter

import framesprite
import pygame
import spritebase
from colors import *
from ships.fighter import Fighter
from ships.bomber import Bomber
from ships.interceptor import Interceptor
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
from helper import clamp, get_nearest
from .planetart import generate_planet_art
from spaceobject import SpaceObject
from funnotification import FunNotification

EMIT_SHIPS_RATE = 0.125
EMIT_CLASSES = {
    'fighter':Fighter,
    'bomber':Bomber,
    'interceptor':Interceptor,
    'alien-fighter':AlienFighter,
    'colonist':Colonist,
    'alien-colonist':AlienColonist,
    'alien-battleship':AlienBattleship
}

RESOURCE_BASE_RATE = 1/220.0

POPULATION_GROWTH_TIME = 30
HP_PER_BUILDING = 10
DEFENSE_RANGE = 30
DESTROY_EXCESS_SHIPS_TIME = 7
PLANET_PROXIMITY = 100

class Planet(SpaceObject):
    HEALTHBAR_SIZE = (30,4)
    def __init__(self, scene, pos, size, resources):
        SpaceObject.__init__(self, scene, pos)
        self.size = size
        self.radius = self.get_radius()
        self.scene = scene
        self.object_type = "planet"        
        self.resources = resources
        self.rotation = random.random() * 6.2818
        self.rotation = 0
        self.rotate_speed = random.random() * 0.5 + 0.125
        self.art = generate_planet_art(
                self.get_radius(),
                self.resources.iron, self.resources.ice, self.resources.gas)
        self.resource_timers = economy.Resources(0,0,0)
        self.owning_civ = None
        self.buildings = []
        self.building_slots = [False] * 12
        self.production = []    

        self.base_angle = 0

        self._population = 0
        self.population_growth_timer = 0

        self.ships = defaultdict(int)
        self.emit_ships_queue = []
        self.emit_ships_timer = 0        

        self.selectable = True
        self.selection_radius = self.size + 14
        self.offset = (0.5, 0.5)
        self._layer = 0
        self.collidable = True
        self.collision_radius = self.size + 8

        self.destroy_excess_ships_timer = 0

        self.needs_panel_update = False

        self._generate_base_frames()
        self.frame = 0        

        self.shipcounter = ShipCounter(self)
        self.scene.ui_group.add(self.shipcounter)
        self.set_health(self.get_max_health())

        ### Upgrades ###
        self.unstable_reaction = 0
        self.owned_time = 0

    @property
    def population(self): return self._population
    @population.setter
    def population(self, value):
        self._population = clamp(value, 0, 999)

    def change_owner(self, civ):
        self.owning_civ = civ
        self.health = max(self.health, self.get_max_health() / 4)
        self._population = min(self._population, 1)
        self.buildings = []
        self.ships = defaultdict(int)
        self.owned_time = 0
        self._generate_base_frames()
        self._generate_frames()

    def get_stat(self, stat):
        owning_civ_stat = 0
        if self.owning_civ:
            owning_civ_stat += self.owning_civ.get_stat(stat)
        return sum([b['building'].stats[stat] for b in self.buildings]) + owning_civ_stat

    def _generate_frame(self, border = False):
        radius = self.size + 8
        padding = 8
        cx,cy = radius + padding, radius + padding
        self._width = radius * 2 + padding * 2
        self._height = radius * 2 + padding * 2
        frame = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        border_radius = 3 if border else 1
        color = self.owning_civ.color if self.owning_civ else PICO_YELLOW

        # Border
        pygame.draw.circle(frame, color, (cx,cy), radius + border_radius)

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            building['building'].draw_outline(frame, color, offset, building['angle'] + self.base_angle,expand=border)

        # Foreground
        #pygame.draw.circle(frame, PICO_GREYPURPLE, (cx,cy), radius)
        #rotated = pygame.transform.rotate(self.art, 0)
        rotated = self.art
        frame.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            building['building'].draw_foreground(frame, offset, building['angle'] + self.base_angle)

        return frame

    def _generate_base_frames(self):
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
        self.art_inactive = inactive
        self.art_hover = hover

    def _generate_frames(self):
        w = self.art_inactive.get_width()
        h = self.art_inactive.get_height()        
        rotated1 = pygame.transform.rotate(self.art_inactive, 0)
        rotated2 = pygame.transform.rotate(self.art_hover, 0)
        s1 = pygame.transform.scale(rotated1, (rotated1.get_width(), rotated1.get_height()))
        s2 = pygame.transform.scale(rotated2, (rotated2.get_width(), rotated2.get_height()))
        w = s1.get_width()
        h = s1.get_height()
        self._sheet = pygame.Surface((w * 2, h), pygame.SRCALPHA)
        self._sheet.blit(s1, (0,0))
        self._sheet.blit(s2, (w,0))
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
        base = 50 + self.size * 30 + len(self.buildings) * HP_PER_BUILDING
        max_hp = base * (1 + self.get_stat("planet_health_mul"))
        if self.get_stat("planet_temp_health_mul"):
            if self.owned_time < 60:
                max_hp *= 1 + self.get_stat("planet_temp_health_mul")      

        if self.get_stat("planet_proximity_health_mul"):
            others = [p for p in self.scene.get_civ_planets(self.owning_civ) if p != self]
            nearest, dist = get_nearest(self.pos, others)
            if dist < PLANET_PROXIMITY ** 2:
                max_hp *= 1 + self.get_stat("planet_proximity_health_mul")
            
        return round(max_hp)

    def get_pop_growth_time(self):
        return POPULATION_GROWTH_TIME / (1 + self.get_stat('pop_growth_rate'))

    def get_max_pop(self):
        return round(self.size * (self.get_stat("pop_max_mul") + 1)) + self.get_stat("pop_max_add")

    def update(self, dt):

        # Emit ships which are queued
        if self.emit_ships_queue:
            self.emit_ships_timer += dt
            if self.emit_ships_timer >= EMIT_SHIPS_RATE:
                ship_type, data = self.emit_ships_queue.pop(0)
                target = data['to']
                towards_angle = (target.pos - self.pos).to_polar()[1]
                towards_angle += random.random() - 0.5
                ship_class = EMIT_CLASSES[ship_type]                                
                off = V2.from_angle(towards_angle)
                s = ship_class(self.scene, self.pos + off * self.get_radius(), self.owning_civ)
                if ship_type in ["colonist", "alien-colonist"]:
                    s.set_pop(data['num'])
                s.set_target(target)
                if 'path' in data:
                    s.set_path(data['path'])
                s.angle = math.atan2(off.y, off.x)
                s.velocity = off * 10
                self.scene.game_group.add(s)
                self.emit_ships_timer -= EMIT_SHIPS_RATE
                self.needs_panel_update = True

        ### Resource production ###
        # Figure out which is the "top" resource
        resource_order = [(a,b) for (a,b) in self.resources.data.items() if b > 0]
        resource_order.sort(key=lambda x:x[1])
        top_resource = resource_order[0][0]
        bottom_resource = resource_order[-1][0]

        for r in self.resources.data.keys():
            rate_modifier = 1

            ### Resource Stats ###

            # Top resource mining rate
            if top_resource == r:
                rate_modifier += self.get_stat("top_mining_rate")
                rate_modifier *= 1 + self.get_stat("top_mining_per_building") * len(self.buildings)

            # Scarcest resource mining rate
            if bottom_resource == r:
                rate_modifier += self.get_stat("scarcest_mining_rate")

            # Unstable Reaction
            rate_modifier *= (1 + self.get_stat("mining_rate") + self.unstable_reaction)

            # Resources mined is based on num workers
            workers = min(self._population, self.size)

            # Add to the timers based on the mining rate
            self.resource_timers.data[r] += dt * self.resources.data[r] * RESOURCE_BASE_RATE * workers * rate_modifier
            v = (self.resources.data[r] / 10.0) # if planet has 100% iron, you get 10 iron every 10 resource ticks.
            if self.resource_timers.data[r] > v:
                self.resource_timers.data[r] -= v
                
                self.owning_civ.earn_resource(r, v)
                if self.owning_civ == self.scene.my_civ:
                    # Add to score!!
                    self.scene.score += v
                    it = IconText(self.pos, None, "+%d" % v, economy.RESOURCE_COLORS[r])
                    it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
                    self.scene.ui_group.add(it)

        # Ship production
        for prod in self.production:
            prod_rate = 1 + self.get_stat("ship_production")
            if prod.ship_type in ['fighter', 'interceptor', 'bomber', 'battleship']:
                prod_rate *= 1 + self.get_stat("%s_production" % prod.ship_type)
            prod.update(self, dt * prod_rate)
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
            if self._population >= 1 - self.get_stat("pop_growth_min_reduction"):
                self.population_growth_timer += dt
                max_pop = self.get_max_pop()
                if self.population_growth_timer >= self.get_pop_growth_time() and self._population < max_pop:
                    self.population_growth_timer = 0
                    self._population += 1
                    self.needs_panel_update = True
                    if self.owning_civ == self.scene.my_civ:
                        it = IconText(self.pos, "assets/i-pop.png", "+1", PICO_GREEN)
                        it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
                        self.scene.ui_group.add(it)

        if self.health <= 0:
            self.buildings = []
            self._population = 0

        # Building stuff
        for b in self.buildings:
            b['building'].update(self, dt)

        # Detect enemies
        threats = self.get_threats()
        if threats:
            for i in range(self.ships[self.get_ship_name("fighter")]):
                self.emit_ship(self.get_ship_name("fighter"), {"to":random.choice(threats)})
            for i in range(self.ships[self.get_ship_name("interceptor")]):
                self.emit_ship(self.get_ship_name("interceptor"), {"to":random.choice(threats)})                
            for i in range(self.ships['alien-battleship']):
                self.emit_ship('alien-battleship', {"to":random.choice(threats)})

        
        #self.rotation += self.rotate_speed * dt * 3
        #self._generate_frames()

        self.upgrade_update(dt)
        super().update(dt)

    def upgrade_update(self, dt):
        if self.get_stat("unstable_reaction") > 0:
            USR = 1 / 60
            # Slowly increase to 1
            self.unstable_reaction = clamp(self.unstable_reaction * (dt * self.get_stat("unstable_reaction") * USR), 0, self.get_stat("unstable_reaction"))

        self.owned_time += dt

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
        return min(self._population, self.size)

    def emit_ship(self, type, data):
        if type in ['colonist', 'alien-colonist']:
            self.emit_ships_queue.append((type, data))
            self._population -= data['num']
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
        b = BUILDINGS[upgrade]()
        self.buildings.append({"building":b, "angle":angle})
        self._generate_base_frames()
        self._generate_frames()
        self.needs_panel_update = True 
        mh_after = self.get_max_health()
        self._health += mh_after - mh_before 
        self.scene.ui_group.add(FunNotification(UPGRADE_CLASSES[b.upgrade].title, self))
        return b

    def add_production(self, order):
        if order.ship_type == "fighter":
            order.number = round(order.number * 1 + self.get_stat("fighter_production_amt"))
            order.number = round(order.number / (2 ** self.get_stat("fighter_production_amt_halving")))
        self.production.append(order)

    def on_health_changed(self, old, new):
        if new < old:
            self.unstable_reaction = 0
        return super().on_health_changed(old, new)