import math
import random
from collections import defaultdict

import bullet
import economy
import explosion
import pygame
import ships.battleship
import ships.bomber
import ships.colonist
import ships.fighter
import ships.interceptor
import sound
import status_effect
from colors import *
from framesprite import FrameSprite
from funnotification import FunNotification
from helper import all_nearby, clamp, get_nearest
from icontext import IconText
from line import IndicatorLine, Line
from ships.all_ships import SHIPS_BY_NAME
from simplesprite import SimpleSprite
from spaceobject import SpaceObject
from v2 import V2

from planet import timeloop
from planet.rewindparticle import RewindParticle
from planet.shipcounter import ShipCounter

from .planetart import generate_planet_art

EMIT_SHIPS_RATE = 0.125

RESOURCE_BASE_RATE = 1/190.0

POPULATION_GROWTH_TIME = 40
POP_GROWTH_IMPROVEMENT_PER_POP = 5
POPULATION_GROWTH_MIN_TIME = 20
HP_PER_BUILDING = 10
DESTROY_EXCESS_SHIPS_TIME = 10
PLANET_PROXIMITY = 130
HAZARD_PROXIMITY = 130

class Planet(SpaceObject):
    HEALTHBAR_SIZE = (30,4)
    DEFENSE_RANGE = 30
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
        self.generate_base_art()
        self.resource_timers = economy.Resources(0,0,0)
        self.owning_civ = None
        self.buildings = []
        self.building_slots = [False] * 12
        self.production = []

        self.upgradeable = True

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

        ## Building juice ##
        self.building_construction_time = 0
        self.last_building = None

        ## Time loop ##
        self.time_loop = False
        self.time_loop_time = 60
        self.last_production = None

        self._generate_base_frames()
        self.frame = 0        
        self.time = 0

        ### Upgrades ###
        self.unstable_reaction = 0
        self.owned_time = 0
        self._timers['regen'] = 0
        self.underground_buildings = {}
        self.planet_weapon_mul = 1
        self._timers['last_launchpad_pop'] = 999
        self._timers['armory'] = 999
        self._timers['headquarters'] = 999
        self._timers['memorial'] = 999
        self._timers['ice_per_docked'] = 0
        self.housing_growth_repeater = 0
        self.housing_growth_timer = 0
        self.housing_max_pop = 0

        self.upgrade_indicators = defaultdict(lambda:None)
        self.created_upgrade_indicators = defaultdict(lambda:None)

        # extra
        self.cinematic_disable = False

        # opt
        self._timers['opt_time'] = random.random()

        self.shipcounter = ShipCounter(self)
        self.scene.ui_group.add(self.shipcounter)

        # warning
        self.warning = FrameSprite(self.pos + V2(-21, -21), "assets/triangle.png", 11)
        self.scene.ui_group.add(self.warning)
        self.warning.visible = False
        self.hide_warnings = False

        self.set_health(self.get_max_health())        

    def __str__(self) -> str:
        return "<Planet %s>" % str(self.pos)

    def generate_base_art(self):
        self.art = generate_planet_art(
                self.get_radius(),
                self.resources.iron, self.resources.ice, self.resources.gas)        

    def set_time_loop(self):
        self.time_loop = True
        self.time_loop_sprite = timeloop.TimeLoop(self.pos + V2(0, 0), "assets/timeloop.png", 13)
        self.time_loop_sprite.offset = (0.5, 0.5)
        self.scene.ui_group.add(self.time_loop_sprite)        

    @property
    def population(self): return self._population
    @population.setter
    def population(self, value):
        self._population = clamp(value, 0, 999)

    def is_buildable(self):
        return len(self.buildings) < 8 and self.get_stat("prevent_buildings") == 0

    def regenerate_art(self):
        self.generate_base_art()
        self._generate_base_frames()

    def is_zero_pop(self):
        return self._population == 0

    def has_extra_ships(self):
        return sum(self.ships.values()) > self.get_max_ships()

    def is_alive(self):
        return self.alive() # pygame alive

    def change_owner(self, civ):
        if self.get_stat("lost_planet_upgrade"):
            r = self.get_primary_resource()
            amt = self.owning_civ.upgrade_limits.data[r]
            self.owning_civ.earn_resource(r, amt, self)
        self.lose_buildings()
        self.owning_civ = civ
        self.upgrade_indicators = defaultdict(lambda:None)
        if civ in self.underground_buildings:
            for building in self.underground_buildings[civ]:
                self.add_building(building['building'].upgrade)
            del self.underground_buildings[civ]

        if civ is not None:
            self.health = max(self.health, self.get_max_health() / 4)
        self._population = 0
        self.emit_ships_queue = []
        self.ships = defaultdict(int)
        self.production = []
        self.last_production = None
        self.owned_time = 0
        self._generate_base_frames()
        self._generate_frames()

    def get_stat(self, stat):
        value = super().get_stat(stat)
        if self.owning_civ:
            value += self.owning_civ.get_stat(stat)
        value += sum([b['building'].stats[stat] for b in self.buildings])
        return value

    def get_base_regen(self):
        regen = self.get_max_health() / 120
        return regen

    def _generate_frame(self, border = False):
        radius = self.size + 8
        padding = 8
        cx,cy = radius + padding, radius + padding
        self._width = radius * 2 + padding * 2
        self._height = radius * 2 + padding * 2
        frame = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        border_radius = 3 if border else 1
        color = self.owning_civ.color if self.owning_civ else PICO_LIGHTGRAY
        if self.owning_civ and not self.owning_civ.is_enemy:
            pygame.draw.circle(frame, color, (cx,cy), radius + border_radius + 2, 1)

        if self.owning_civ and self.owning_civ.is_enemy:
            num_spikes = 8 #clamp(radius + 12, 16, 24)
            pts = []
            for i in range(num_spikes * 2 + 1):
                theta = i * 6.2818 / (num_spikes * 2)
                rad = radius + border_radius + 2
                if i % 2 == 1:
                    #pygame.draw.circle(frame, color, (V2.from_angle(theta) * (rad-2) + V2(cx + 0,cy + 0)).tuple_round(), 1, 0)
                    rad = radius + border_radius - 1
                pts.append((V2.from_angle(theta) * rad + V2(cx,cy)).tuple_int())

            #pygame.draw.lines(frame, color, False, pts, 1)
            pygame.draw.polygon(frame, color, pts, 0)

        # Border
        pygame.draw.circle(frame, color, (cx,cy), radius + border_radius)

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            b = building['building']
            c = 0
            if b == self.last_building and self.building_construction_time > 0:
                c = self.building_construction_time
            b.draw_outline(frame, color, offset, building['angle'] + self.base_angle, expand=border, construction = c)

        # Foreground
        #pygame.draw.circle(frame, PICO_GREYPURPLE, (cx,cy), radius)
        #rotated = pygame.transform.rotate(self.art, 0)
        rotated = self.art
        frame.blit(rotated, (cx - rotated.get_width() // 2, cy - rotated.get_height() // 2))

        for building in self.buildings:
            offset = V2.from_angle(building['angle'] + self.base_angle) * radius + V2(cx, cy)
            b = building['building']
            c = 0
            if b == self.last_building and self.building_construction_time > 0:
                c = self.building_construction_time            
            b.draw_foreground(frame, offset, building['angle'] + self.base_angle, construction=c)

        if self.building_construction_time > 2.75:
            pygame.draw.circle(frame, PICO_WHITE, (cx,cy), radius)

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

    def get_max_shield(self):
        return self.get_stat("planet_shield")

    def get_max_health(self):
        hp_per_building = HP_PER_BUILDING * (1 + self.get_stat("planet_health_per_construct"))
        base = 25 + self.size * 15 + len(self.buildings) * hp_per_building
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
        rate = 1 + self.get_stat('pop_growth_rate')
        rate *= 1 + (self.get_stat("pop_growth_rate_per_docked_ship") * sum(self.ships.values()))
        if sum(self.ships.values()) == 0:
            rate *= 1 + (self.get_stat("pop_growth_without_ships"))
        growth_time = max(POPULATION_GROWTH_TIME - POP_GROWTH_IMPROVEMENT_PER_POP * self.population, POPULATION_GROWTH_MIN_TIME)
        return growth_time / rate

    def get_max_pop(self):
        return round(self.size * (self.get_stat("pop_max_mul") + 1)) + self.get_stat("pop_max_add") + self.housing_max_pop

    def update(self, dt):
        real_dt = dt
        if self._timers['opt_time'] > 0.25:
            self._timers['opt_time'] -= 0.25
            dt = 0.25
        else:
            return super().update(real_dt)

        self.time += dt
        if self.time < 1:
            self.set_health(self.get_max_health())

        self.warning.visible = (
            (self.is_zero_pop() or self.has_extra_ships()) and 
            (self.owning_civ and not self.owning_civ.is_enemy) and
            not self.hide_warnings
        )
        if self.warning.visible:
            self.warning.frame = int((self.time * 2) % 2)

        # Emit ships which are queued
        if self.emit_ships_queue:
            self.emit_ships_timer += dt
            if self.emit_ships_timer >= EMIT_SHIPS_RATE:
                ship_type, data = self.emit_ships_queue.pop(0)
                target = data['to']

                if self.get_stat("launchpad_pop_chance"):
                    if target.owning_civ != self.owning_civ and ship_type == "colonist":
                        if self._timers['last_launchpad_pop'] >= 20 and random.random() < self.get_stat("launchpad_pop_chance"):
                            self._timers['last_launchpad_pop'] = 0
                            self.add_population(1)

                if self.get_stat("launchpad_fighter_chance"):
                    if target.owning_civ and target.owning_civ != self.owning_civ and ship_type in ["bomber","interceptor"]:
                        if random.random() < self.get_stat("launchpad_fighter_chance"):
                            self.add_ship("fighter")

                if self.get_stat("launchpad_battleship_health"):
                    if target.owning_civ and target.owning_civ != self.owning_civ and ship_type == "battleship":
                        self.health += self.get_stat("launchpad_battleship_health")

                if self.get_stat("launchpad_battleship_pop"):
                    if target.owning_civ and target.owning_civ != self.owning_civ and ship_type == "battleship":
                        self.add_population(self.get_stat("launchpad_battleship_pop"))
                
                towards_angle = (target.pos - self.pos).to_polar()[1]
                towards_angle += random.random() - 0.5
                ship_class = SHIPS_BY_NAME[ship_type]                                
                off = V2.from_angle(towards_angle)
                s = ship_class(self.scene, self.pos + off * self.get_radius(), self.owning_civ)
                if 'colonist' in ship_type:
                    s.set_pop(data['num'])
                s.origin = self
                s.set_target(target)
                s.angle = math.atan2(off.y, off.x)
                s.velocity = off * 10
                if 'defending' in data:
                    s.defending = data['defending']
                self.scene.game_group.add(s)
                self.emit_ships_timer -= EMIT_SHIPS_RATE
                self.needs_panel_update = True
                sound.play("launch")

                # Any effects to attach to the ship
                if self.get_stat("ship_pop_boost"):
                    for i in range(self.population):
                        s.add_effect(status_effect.ShipBoostEffect(s, self))

        ### Resource production ###
        # Figure out which is the "top" resource
        resource_order = [(a,b) for (a,b) in self.resources.data.items() if b > 0]
        resource_order.sort(key=lambda x:x[1])
        top_resource = resource_order[0][0]
        bottom_resource = resource_order[-1][0]

        for r in self.resources.data.keys():
            rate_modifier = 1

            ### Resource Stats ###

            if top_resource == r:
                rate_modifier += self.get_stat("top_mining_rate")
                rate_modifier *= 1 + self.get_stat("top_mining_per_building") * len(self.buildings)

            if bottom_resource == r:
                rate_modifier += self.get_stat("scarcest_mining_rate")

            rate_modifier *= (1 + self.get_stat("mining_rate") + self.unstable_reaction)

            if r == "ice" and self.get_stat("ice_mining_rate"):
                rate_modifier *= 1 + self.get_stat("ice_mining_rate")

            if r == "gas" and self.get_stat("gas_mining_rate"):
                rate_modifier *= 1 + self.get_stat("gas_mining_rate")

            if self.get_stat("mining_rate_first_120") and self.owned_time < 120:
                rate_modifier *= self.get_stat("mining_rate_first_120")

            if self.get_stat("mining_rate_proximity"):
                _, distsq = get_nearest(self.pos,self.scene.get_hazards())
                if distsq < HAZARD_PROXIMITY ** 2:
                    rate_modifier *= 1 + self.get_stat("mining_rate_proximity")

            if self._population >= self.get_max_pop():
                rate_modifier *= 1 + self.get_stat("mining_rate_at_max_pop")

            # Resources mined is based on num workers
            workers = min(self._population, self.get_max_pop())

            # Add to the timers based on the mining rate
            self.resource_timers.data[r] += dt * self.resources.data[r] * RESOURCE_BASE_RATE * workers * rate_modifier
            v = (self.resources.data[r] / 10.0) # if planet has 100% iron, you get 10 iron every 10 resource ticks.
            if self.resources.data[r] > 0 and self.resource_timers.data[r] > v:
                self.resource_timers.data[r] -= v
                self.owning_civ.earn_resource(r, v, where=self)
                if self.get_stat("mining_ice_per_iron"):
                    self.owning_civ.earn_resource("ice", v * self.get_stat("mining_ice_per_iron"), where=self)
                if self.get_stat("mining_gas_per_iron"):
                    self.owning_civ.earn_resource("gas", v * self.get_stat("mining_gas_per_iron"), where=self)

        # Ship production
        for prod in self.production:
            prod_rate = 1 + self.get_stat("ship_production")
            prod_amt_mul = 1

            prod_rate *= 1 + self.get_stat("ship_production_rate_per_pop") * self.population

            if prod.ship_type == "fighter":
                prod_amt_mul += self.get_stat("fighter_production_amt")
                prod_amt_mul /= (2 ** self.get_stat("fighter_production_amt_halving"))
            
            if prod.ship_type in ['fighter', 'scout', 'interceptor', 'bomber', 'battleship']:
                prod_rate *= 1 + self.get_stat("%s_production" % prod.ship_type)

            self.upgrade_indicators['ship_production_proximity'] = None
            if self.get_stat("ship_production_proximity"):
                enemy_planets = self.scene.get_enemy_planets(self.owning_civ)
                nearest, dist = get_nearest(self.pos, enemy_planets)
                if dist < PLANET_PROXIMITY ** 2:
                    prod_rate *= 1 + self.get_stat("ship_production_proximity")
                    self.upgrade_indicators['ship_production_proximity'] = nearest
                    

            prod.number_mul = prod_amt_mul
            prod.update(self, dt * prod_rate)
        self.production = [p for p in self.production if not p.done]

        # Time loop
        if self.time_loop:
            self.time_loop_time -= dt
            if self.time_loop_time < 0:
                self.time_loop_time += 60
                if self.last_production:
                    self.add_ship(self.last_production)
                self.scene.ui_group.add(RewindParticle(self.pos, self.radius))

        # Ship destruction
        
        if sum(self.ships.values()) > self.get_max_ships():
            self.destroy_excess_ships_timer += dt
            if self.destroy_excess_ships_timer >= DESTROY_EXCESS_SHIPS_TIME:
                # First try to get rid of fighters, than any advanced ships, then battleships if nothing else existed
                if self.ships['fighter'] > 0:
                    self.ships['fighter'] -= 1
                    destroyed_ship = "fighter"
                else:
                    for ship_name in self.ships.keys():
                        if ship_name not in ['fighter', 'battleship']:
                            if self.ships[ship_name] > 0:
                                self.ships[ship_name] -= 1
                                destroyed_ship = ship_name
                                break

                    else:
                        if self.ships['battleship'] > 0:
                            self.ships['battleship'] -= 1
                            destroyed_ship = "battleship"

                if self.owning_civ is None or self.owning_civ.is_player:
                    it = IconText(self.pos, "assets/i-%s.png" % destroyed_ship, "-1", PICO_PINK)
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
                    self.add_population(1)

        # Building stuff
        for b in self.buildings:
            b['building'].update(self, dt)

        if self.building_construction_time > 0:
            self.building_construction_time -= dt
            self._generate_base_frames()
            self._generate_frames()

        # Detect enemies
        if not self.cinematic_disable:
            threats = self.get_threats()
            if threats:
                self.defend_planet_against(threats)
                
        self.upgrade_update(dt)
        self.special_update(dt)
        super().update(real_dt)

    def special_update(self, dt):
        pass

    def upgrade_update(self, dt):
        if self.get_stat("unstable_reaction") > 0:
            USR = 1 / 60
            # Slowly increase to 1
            self.unstable_reaction = clamp(self.unstable_reaction * (dt * self.get_stat("unstable_reaction") * USR), 0, self.get_stat("unstable_reaction"))

        REGEN_TIMER = 5
        if self._timers['regen'] > REGEN_TIMER:
            self._timers['regen'] = 0
            self.health += self.get_base_regen() * REGEN_TIMER
            if self.get_stat("regen") > 0:
                self.health += self.get_stat("regen") * REGEN_TIMER
            if self.get_stat("deserted_regen") > 0 and self.population == 0:
                self.health += self.get_stat("deserted_regen") * REGEN_TIMER
            if self.get_stat("planet_regen_without_ships") and sum(self.ships.values()) == 0:
                self.health += self.get_stat("planet_regen_without_ships") * REGEN_TIMER

        
            # o2 degeneration
            if self.scene.game.run_info.o2 <= 0 and self.owning_civ and self.owning_civ.is_player:
                self.health -= self.get_base_regen() * REGEN_TIMER
                self.health -= 1 * REGEN_TIMER

        if self.get_stat("ice_per_docked") > 0:
            if self._timers['ice_per_docked'] > 5:
                self._timers['ice_per_docked'] -= 5
                docked = sum(self.ships.values())
                self.owning_civ.earn_resource("ice", self.get_stat("ice_per_docked") * docked, where = self.pos)

        self.owned_time += dt

        self.planet_weapon_mul = 1
        if self.population == 0:
            self.planet_weapon_mul += self.get_stat("planet_weapon_boost_zero_pop")

        if sum(self.ships.values()) == 0:
            self.planet_weapon_mul += self.get_stat("planet_weapon_boost_zero_ships")

        self.planet_weapon_mul += self.get_stat("planet_weapon_boost") 

        if self.get_stat("planet_slow_aura"):
            enemy_ships = set(self.scene.get_enemy_ships(self.owning_civ))
            near = set(all_nearby(self.pos, enemy_ships, 80))
            far = enemy_ships - near
            for ship in near:
                ship.slow_aura = self.get_stat("planet_slow_aura")
            for ship in far:
                ship.slow_aura = 0

        if self.get_stat("max_pop_growth") and self.housing_growth_timer < self.get_stat("max_pop_growth") and not self.owning_civ.housing_colonized:
            self.housing_growth_timer += dt
            self.housing_growth_repeater += dt
            if self.housing_growth_repeater >= 30:
                self.housing_growth_repeater = 0
                self.housing_max_pop += 1

        self.upgrade_indicators['ship_production_proximity'] = None
        if self.get_stat("ship_production_proximity"):
            enemy_planets = self.scene.get_enemy_planets(self.owning_civ)
            nearest, dist = get_nearest(self.pos, enemy_planets)
            if dist < PLANET_PROXIMITY ** 2:
                self.upgrade_indicators['ship_production_proximity'] = nearest               

        self.upgrade_indicators['mining_rate_proximity'] = None
        if self.get_stat("mining_rate_proximity"):
            nearest, distsq = get_nearest(self.pos,self.scene.get_hazards())
            if distsq < HAZARD_PROXIMITY ** 2:
                self.upgrade_indicators['mining_rate_proximity'] = nearest               

        for key in list(self.upgrade_indicators.keys()) + list(self.created_upgrade_indicators.keys()):
            if self.upgrade_indicators[key] and not self.created_upgrade_indicators[key]:
                self.create_indicator(key)
            elif self.created_upgrade_indicators[key] and not self.upgrade_indicators[key]:
                self.created_upgrade_indicators[key].kill()
                self.created_upgrade_indicators[key] = None

    def create_indicator(self, key):
        print("create indicator", key)
        if key == "ship_production_proximity":
            obj = IndicatorLine(self, self.pos, self.upgrade_indicators[key].pos, PICO_RED, name="Proximity Alert")
            self.scene.ui_group.add(obj)
            self.created_upgrade_indicators[key] = obj
        if key == "mining_rate_proximity":
            obj = IndicatorLine(self, self.pos, self.upgrade_indicators[key].pos, PICO_LIGHTGRAY, name="Space Mining")
            self.scene.ui_group.add(obj)
            self.created_upgrade_indicators[key] = obj            

    def get_primary_resource(self):
        resource_order = [(a,b) for (a,b) in self.resources.data.items() if b > 0]
        resource_order.sort(key=lambda x:x[1])
        return resource_order[0][0]        

    def on_die(self):  
        sound.play("explosion2")
        if self.get_stat("underground"):
            for ship in all_nearby(self.pos, self.scene.get_enemy_ships(self.owning_civ), 60):
                ship.take_damage(20 * self.get_stat("underground"), self)
                e = explosion.Explosion(self.pos, [PICO_WHITE], 1, 60)
                self.scene.game_group.add(e)
        self.change_owner(None)
        
    def emitted_ship_died(self, ship):
        if self.get_stat("memorial") and self._timers['memorial'] >= 20:
            self.add_ship("fighter")
            self._timers['memorial'] = 0

    def emitted_ship_colonized(self, ship, planet):
        if self.get_stat("headquarters") and self._timers['headquarters'] >= 30:
            self.add_population(1)
            self._timers['headquarters'] = 0

    def add_population(self, num, force_show=False):
        self._population = max(self._population + num, 0)
        self.needs_panel_update = True
        if force_show or self.owning_civ and self.owning_civ.is_player:
            if num > 0:
                t = "+%d" % num
            else:
                t = "%d" % num
            it = IconText(self.pos, "assets/i-pop.png", t, PICO_GREEN)
            it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
            self.scene.ui_group.add(it)        

    def get_max_ships(self):
        s = round(self.get_max_pop() * (self.get_stat("max_ships_mul") + 1))
        hard_max = self.get_stat("max_ships_per_planet")
        if hard_max > 0:
            s = min(s, hard_max)
        return s

    def get_threats(self):
        enemy_ships = self.scene.get_enemy_ships(self.owning_civ)
        ret = []
        for s in enemy_ships:
            dist = (s.pos - self.pos).sqr_magnitude()
            if dist < (self.get_radius() + self.DEFENSE_RANGE) ** 2:        
                ret.append(s)
        return ret

    def get_workers(self):
        return min(self._population, self.get_max_pop())

    def emit_ship(self, type, data):
        if 'colonist' in type:
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
        if self.owning_civ and self.owning_civ.is_player:
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
        b = upgrade.building()
        self.buildings.append({"building":b, "angle":angle})
        self.last_building = b
        self.building_construction_time = 3        
        self._generate_base_frames()
        self._generate_frames()
        self.needs_panel_update = True 
        mh_after = self.get_max_health()
        self._health += mh_after - mh_before 
        if self.owning_civ and self.owning_civ.is_player:
            self.scene.ui_group.add(FunNotification(upgrade.title, self))
        return b

    def add_production(self, order):
        self.production.append(order)

    def on_health_changed(self, old, new):
        if new < old:
            self.unstable_reaction = 0
        return super().on_health_changed(old, new)

    def take_damage(self, damage, origin=None):
        if self.get_stat("damage_iron"):
            self.owning_civ.earn_resource("iron", self.get_stat("damage_iron"), where=self)
        pre_health = self.health

        if self.get_stat("armory") and self._timers['armory'] > 10:
            self._timers['armory'] = 0
            self.add_population(-1)
            self.add_ship("fighter")

        if origin and isinstance(origin, bullet.Bullet):
            if origin.shooter and isinstance(origin.shooter, ships.ship.Ship):
                self.defend_planet_against([origin.shooter])

        return_val = super().take_damage(damage, origin=origin)
        return return_val

    def defend_planet_against(self, threats):
        for ship_name in self.ships.keys():
            if ship_name not in ['bomber']:
                for i in range(self.ships[ship_name]):
                    self.emit_ship(ship_name, {"to":random.choice(threats), "defending":self})

    def blow_up_buildings(self):
        for building in self.buildings:
            bp = V2.from_angle(building['angle'] + self.base_angle) * self.get_radius() + self.pos
            e = explosion.Explosion(bp, [PICO_WHITE, PICO_LIGHTGRAY, PICO_DARKGRAY], 0.25, 11, scale_fn="log", line_width=1)
            self.scene.game_group.add(e)        
            building['building'].kill()
        self._generate_base_frames()
        self._generate_frames()

    def raze_building(self):
        if not self.buildings:
            return

        bi = random.randint(0, len(self.buildings)-1)
        b = self.buildings[bi]
        b['building'].kill()
        bp = V2.from_angle(b['angle'] + self.base_angle) * self.get_radius() + self.pos
        e = explosion.Explosion(bp, [PICO_WHITE, PICO_LIGHTGRAY, PICO_DARKGRAY], 0.25, 11, scale_fn="log", line_width=1)
        self.scene.game_group.add(e)  
        self.buildings.pop(bi)
        self._generate_base_frames()
        self._generate_frames()        

    def lose_buildings(self):
        if self.get_stat("underground"):
            self.underground_buildings[self.owning_civ] = self.buildings
            for building in self.buildings:
                building['building'].kill()
        else:
            self.blow_up_buildings()

        self.buildings = []
        self._generate_base_frames()
        self._generate_frames()        
