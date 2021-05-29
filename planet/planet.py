from aliens.alien2colonist import Alien2Colonist
from aliens.alien2controlship import Alien2ControlShip
from aliens.alien2fighter import Alien2Fighter
from aliens.alien1warpship import Alien1WarpShip
from aliens.alien2battleship import Alien2Battleship
import math
import random
from upgrade.upgrades import UPGRADE_CLASSES
from aliens.alien1colonist import Alien1Colonist
from aliens.alien1fighter import Alien1Fighter
from aliens.alien1battleship import Alien1Battleship

import framesprite
import pygame
import spritebase
from colors import *
from ships.fighter import Fighter
from ships.bomber import Bomber
from ships.interceptor import Interceptor
from ships.colonist import Colonist
from ships.battleship import Battleship
from ships.ship import Ship
from v2 import V2
from meter import Meter
from healthy import Healthy
import economy
import text
from planet.shipcounter import ShipCounter
from icontext import IconText
from collections import defaultdict
from helper import all_nearby, clamp, get_nearest
from .planetart import generate_planet_art
from spaceobject import SpaceObject
from funnotification import FunNotification
import explosion

EMIT_SHIPS_RATE = 0.125
EMIT_CLASSES = {
    'fighter':Fighter,
    'bomber':Bomber,
    'interceptor':Interceptor,
    'battleship':Battleship,
    'colonist':Colonist,
    'alien1fighter':Alien1Fighter,
    'alien1colonist':Alien1Colonist,
    'alien1battleship':Alien1Battleship,
    'alien1warpship':Alien1WarpShip,
    'alien2fighter':Alien2Fighter,
    'alien2controlship':Alien2ControlShip,
    'alien2colonist':Alien2Colonist,
    'alien2battleship':Alien2Battleship
}

RESOURCE_BASE_RATE = 1/220.0

POPULATION_GROWTH_TIME = 40
POP_GROWTH_IMPROVEMENT_PER_POP = 5
POPULATION_GROWTH_MIN_TIME = 20
HP_PER_BUILDING = 10
DESTROY_EXCESS_SHIPS_TIME = 7
PLANET_PROXIMITY = 100
HAZARD_PROXIMITY = 70

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
        self._timers['regen'] = 0
        self.underground_buildings = {}
        self.planet_weapon_mul = 1
        self.in_comm_range = False
        self._timers['last_launchpad_pop'] = 20

        # opt
        self._timers['opt_time'] = random.random()

    def __str__(self) -> str:
        return "<Planet %s>" % str(self.pos)

    @property
    def population(self): return self._population
    @population.setter
    def population(self, value):
        self._population = clamp(value, 0, 999)

    def regenerate_art(self):
        self.art = generate_planet_art(
                self.get_radius(),
                self.resources.iron, self.resources.ice, self.resources.gas)
        self._generate_base_frames()

    def is_alive(self):
        return self.alive() # pygame alive

    def change_owner(self, civ):
        self.lose_buildings()
        self.owning_civ = civ
        if civ in self.underground_buildings:
            for building in self.underground_buildings[civ]:
                self.add_building(building.upgrade)
            del self.underground_buildings[civ]
        self.health = max(self.health, self.get_max_health() / 4)
        self._population = 0
        self.ships = defaultdict(int)
        self.production = []
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

    def get_max_shield(self):
        return self.get_stat("planet_shield")

    def get_max_health(self):
        hp_per_building = HP_PER_BUILDING * (1 + self.get_stat("planet_health_per_construct"))
        base = 50 + self.size * 30 + len(self.buildings) * hp_per_building
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
        growth_time = max(POPULATION_GROWTH_TIME - POP_GROWTH_IMPROVEMENT_PER_POP * self.population, POPULATION_GROWTH_MIN_TIME)
        return growth_time / rate

    def get_max_pop(self):
        return round(self.size * (self.get_stat("pop_max_mul") + 1)) + self.get_stat("pop_max_add")

    def update(self, dt):
        real_dt = dt
        if self._timers['opt_time'] > 0.25:
            self._timers['opt_time'] -= 0.25
            dt = 0.25
        else:
            return super().update(real_dt)


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
                ship_class = EMIT_CLASSES[ship_type]                                
                off = V2.from_angle(towards_angle)
                s = ship_class(self.scene, self.pos + off * self.get_radius(), self.owning_civ)
                if 'colonist' in ship_type:
                    s.set_pop(data['num'])
                s.set_target(target)
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

            if self.get_stat("mining_rate_proximity"):
                _, distsq = get_nearest(self.pos,self.scene.get_hazards())
                if distsq < HAZARD_PROXIMITY ** 2:
                    rate_modifier *= 1 + self.get_stat("mining_rate_proximity")

            if self._population >= self.size:
                rate_modifier *= 1 + self.get_stat("mining_rate_at_max_pop")

            # Resources mined is based on num workers
            workers = min(self._population, self.size)

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

            if prod.ship_type in ['fighter', 'interceptor', 'bomber', 'battleship']:
                prod_rate *= 1 + self.get_stat("%s_production" % prod.ship_type)

            if self.get_stat("ship_production_proximity"):
                enemy_planets = self.scene.get_enemy_planets(self.owning_civ)
                if get_nearest(self.pos, enemy_planets)[1] < PLANET_PROXIMITY ** 2:
                    prod_rate *= 1 + self.get_stat("ship_production_proximity")
                    
            prod.update(self, dt * prod_rate)
        self.production = [p for p in self.production if not p.done]

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

                if self.owning_civ == self.scene.my_civ:
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

        if self.health <= 0:
            self.lose_buildings()
            self._population = 0
            self._generate_base_frames()
            self._generate_frames()            

        # Building stuff
        for b in self.buildings:
            b['building'].update(self, dt)

        # Detect enemies
        threats = self.get_threats()
        if threats:
            for ship_name in self.ships.keys():
                if ship_name not in ['bomber']:
                    for i in range(self.ships[ship_name]):
                        self.emit_ship(ship_name, {"to":random.choice(threats)})

        
        #self.rotation += self.rotate_speed * dt * 3
        #self._generate_frames()

        self.upgrade_update(dt)
        super().update(real_dt)

    def upgrade_update(self, dt):
        if self.get_stat("unstable_reaction") > 0:
            USR = 1 / 60
            # Slowly increase to 1
            self.unstable_reaction = clamp(self.unstable_reaction * (dt * self.get_stat("unstable_reaction") * USR), 0, self.get_stat("unstable_reaction"))

        REGEN_TIMER = 5
        if self._timers['regen'] > REGEN_TIMER:
            self._timers['regen'] = 0
            if self.get_stat("regen") > 0:
                self.health += self.get_stat("regen") * REGEN_TIMER
            if self.get_stat("deserted_regen") > 0 and self.population == 0:
                self.health += self.get_stat("deserted_regen") * REGEN_TIMER
            if self.get_stat("planet_regen_without_ships") and sum(self.ships.values()) == 0:
                self.health += self.get_stat("planet_regen_without_ships") * REGEN_TIMER

        self.owned_time += dt

        if self.population == 0:
            self.planet_weapon_mul = (1 + self.get_stat("planet_weapon_boost_zero_pop"))
        else:
            self.planet_weapon_mul = 1

        if self.get_stat("planet_slow_aura"):
            enemy_ships = set(self.scene.get_enemy_ships(self.owning_civ))
            near = set(all_nearby(self.pos, enemy_ships, 80))
            far = enemy_ships - near
            for ship in near:
                ship.slow_aura = self.get_stat("planet_slow_aura")
            for ship in far:
                ship.slow_aura = 0


    def add_population(self, num):
        self._population += num
        self.needs_panel_update = True
        if self.owning_civ == self.scene.my_civ:
            it = IconText(self.pos, "assets/i-pop.png", "+1", PICO_GREEN)
            it.pos = self.pos + V2(0, -self.get_radius() - 5) - V2(it.width, it.height) * 0.5 + V2(random.random(), random.random()) * 15
            self.scene.ui_group.add(it)        

    def get_max_ships(self):
        return self.get_max_pop()

    def get_threats(self):
        enemy_ships = self.scene.get_enemy_ships(self.owning_civ)
        ret = []
        for s in enemy_ships:
            dist = (s.pos - self.pos).sqr_magnitude()
            if dist < (self.get_radius() + self.DEFENSE_RANGE) ** 2:        
                ret.append(s)
        return ret

    def get_workers(self):
        return min(self._population, self.size)

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
        b = upgrade.building()
        self.buildings.append({"building":b, "angle":angle})
        self._generate_base_frames()
        self._generate_frames()
        self.needs_panel_update = True 
        mh_after = self.get_max_health()
        self._health += mh_after - mh_before 
        if self.owning_civ == self.scene.my_civ:
            self.scene.ui_group.add(FunNotification(upgrade.title, self))
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

    def take_damage(self, damage, origin):
        if self.get_stat("damage_iron"):
            self.owning_civ.earn_resource("iron", self.get_stat("damage_iron"), where=self)
        return super().take_damage(damage, origin=origin)

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