from satellite import ReflectorShield, SpaceStation
from rangeindicator import RangeIndicator
from v2 import V2
from colors import *
import pygame
from bullet import Bullet
import random
from stats import Stats
import json
from helper import all_nearby

class Building:
    upgrade = None
    def __init__(self):
        self.shapes = []
        self.stats = Stats()

    def load_shapes(self, name):
        data = json.load(open("assets/buildings/%s.json" % name))
        self.shapes = [
            ([V2(*pt) for pt in shape[0]], shape[1]) for shape in data
        ]

    def update(self, planet, dt):
        pass

    def draw_shape(self, surface, shape, color, offset, angle, expand=False):
        angle += 3.14159 / 2
        center = offset
        for pt in shape:
            center += pt * (1 / len(shape))
        final_pts = []
        for pt in shape:
            dist,ang = pt.to_polar()
            ang += angle
            new_pt = V2.from_angle(ang) * dist * 1.25 + offset
            if expand:
                new_pt += (new_pt - center).normalized() * .75
            final_pts.append(new_pt)
        
        pygame.draw.polygon(surface, color, [pt.tuple() for pt in final_pts], 0)


    def draw_foreground(self, surface, offset, angle):
        for points, color in self.shapes:
            self.draw_shape(surface, points, color, offset, angle)

    def draw_outline(self, surface, color, offset, angle, expand=False):
        for points, _ in self.shapes:
            self.draw_shape(surface, points, color, offset + V2(-1,0), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(+1,0), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(0,-1), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(0,+1), angle, expand)

    def kill(self):
        pass

def make_simple_stats_building(stats=None, shape=None):
    class AdHocBuilding(Building):
        def __init__(self):
            super().__init__()
            self.load_shapes(shape)
            self.stats = stats

    return AdHocBuilding

class ArmoryBuilding(Building):
    FIRE_RATE = 5
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.fire_time = 0
        
    def update(self, planet, dt):
        self.fire_time += dt
        threats = planet.get_threats()
        if self.fire_time > self.FIRE_RATE and threats:
            self.fire_time = 0
            for i in range(planet.population):
                angle = random.random() * 6.2818
                b = Bullet(
                    planet.pos + V2.from_angle(angle) * planet.get_radius(),
                    random.choice(threats), 
                    planet, vel=V2.from_angle(angle) * 20, mods={'homing':1, "damage_base":3 * planet.planet_weapon_mul, "color":PICO_WHITE, "life":5}
                    )
                planet.scene.game_group.add(b)

class SSMBatteryBuilding(Building):
    FIRE_RATE = 2.5
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.fire_time = 0
        
    def update(self, planet, dt):
        self.fire_time += dt
        threats = planet.get_threats()
        if self.fire_time > self.FIRE_RATE and threats:
            t = random.choice(threats)
            delta = t.pos - planet.pos
            _, angle = delta.to_polar()
            angle += random.random() * 1.5 - 0.75            
            self.fire_time = 0
            b = Bullet(
                planet.pos + V2.from_angle(angle) * planet.get_radius(),
                t, 
                planet, vel=V2.from_angle(angle) * 20, mods={
                        'homing':1, "damage_base":10 * planet.planet_weapon_mul, "blast_radius":10, "color":PICO_WHITE, "life":5, "missile_speed":0.5
                    }
                )
            planet.scene.game_group.add(b)

class InterplanetarySSMBatteryBuilding(Building):
    FIRE_RATE = 2.5
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.fire_time = 0
        
    def update(self, planet, dt):
        self.fire_time += dt
        threats = [
            o for o in planet.scene.get_enemy_objects(planet.owning_civ)
            if (o.pos - planet.pos).sqr_magnitude() < 100 ** 2 and o.health > 0
        ]
        if self.fire_time > self.FIRE_RATE and threats:
            self.fire_time = 0
            t = random.choice(threats)
            delta = t.pos - planet.pos
            _, angle = delta.to_polar()
            angle += random.random() * 1.5 - 0.75
            b = Bullet(
                planet.pos + V2.from_angle(angle) * planet.get_radius(),
                t, 
                planet, vel=V2.from_angle(angle) * 20, mods={
                        'homing':1, "damage_base":10 * planet.planet_weapon_mul, "blast_radius":10, "color":PICO_WHITE, "life":5, "missile_speed":0.5
                    }
                )
            planet.scene.game_group.add(b)              

class EMGeneratorBuilding(Building):
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.stunned_ships = {}
        self.indicator = None
        
    def update(self, planet, dt):
        if not self.indicator:
            self.indicator = RangeIndicator(planet.pos, planet.DEFENSE_RANGE + planet.get_radius(), PICO_BLUE, line_length=2, line_space=5)
            planet.scene.game_group.add(self.indicator)
        threats = planet.get_threats()
        for ship in threats:
            if ship not in self.stunned_ships:
                ship.set_state("stunned")
                self.stunned_ships[ship] = True

    def kill(self):
        if self.indicator:
            self.indicator.kill()
        Building.kill(self)

class SatelliteBuilding(Building):
    SATELLITE_CLASS = None
    def __init__(self):
        super().__init__()
        self.load_shapes("armory")
        self.satellite = None

    def update(self, planet, dt):
        if self.satellite is None:
            self.satellite = self.SATELLITE_CLASS(planet.scene, planet)
            planet.scene.game_group.add(self.satellite)
        return super().update(planet, dt)

    def kill(self):
        self.satellite.kill()
        super().kill()

class SpaceStationBuilding(SatelliteBuilding):
    SATELLITE_CLASS = SpaceStation
    def __init__(self):
        super().__init__()
        self.stats = Stats(pop_max_add=4)

class ReflectorShieldBuilding(SatelliteBuilding):
    SATELLITE_CLASS = ReflectorShield


# Laser - planet_weapon_mul

class AlienHomeDefenseBuilding(Building):
    FIRE_RATE = 0.40
    upgrade = "alienhomedefense"
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.stats = Stats(planet_health_mul=1)
        self.fire_time = 0
        
    def update(self, planet, dt):
        # Regenerate
        planet.health += 1 * dt
        # Fire at threats
        self.fire_time += dt
        threats = planet.get_threats()
        if self.fire_time > self.FIRE_RATE and threats:
            self.fire_time = 0
            threat = random.choice(threats)
            _,angle = (threat.pos - planet.pos).to_polar()
            angle += random.random() * 0.5 - 0.25
            b = Bullet(
                planet.pos + V2.from_angle(angle) * planet.get_radius(),
                threat, 
                planet, vel=V2.from_angle(angle) * 20, mods={'homing':1, "color":PICO_RED},
                )
            planet.scene.game_group.add(b)

class AuraBuilding(Building):
    def __init__(self):
        super().__init__()
        self.targeting = "enemy"
        self.applied_ships = set()

    def update(self, planet, dt):
        if self.targeting == "enemy":
            ships = set(planet.scene.get_enemy_ships(planet.owning_civ))
        elif self.targeting == "mine":
            ships = set(planet.scene.get_my_ships(planet.owning_civ))
        else:
            ships = set([])
        near = set(all_nearby(planet.pos, ships, 80))
        far = ships - near
        for ship in near:
            if ship not in self.applied_ships:
                self.apply(ship)
                self.applied_ships.add(ship)

        for ship in far:
            if ship in self.applied_ships:
                self.unapply(ship)
                self.applied_ships.remove(ship)

        return super().update(planet, dt)     

    def apply(self, ship):
        pass

    def unapply(self, ship):
        pass   

class LowOrbitDefensesBuilding(AuraBuilding):
    def __init__(self):
        super().__init__()
        self.targeting = "mine"

    def apply(self, ship):
        ship.bonus_max_health_aura += 10

    def unapply(self, ship):
        ship.bonus_max_health_aura -= 10

class DefenseMatrix(Building):
    pass #impl

class DefenseMatrixAlpha(DefenseMatrix):
    pass #impl

class DefenseMatrixOmega(DefenseMatrix):
    pass #impl

class Portal(Building):
    pass #impl

class ClockwisePortal(Portal):
    pass #impl

class CounterClockwisePortal(Portal):
    pass #impl