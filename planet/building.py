import json
import random

import bullet
import laserparticle
import pygame
import status_effect
from colors import *
from helper import all_nearby
from line import Line
from rangeindicator import RangeIndicator
from resources import resource_path
from satellite import (OffWorldMining, OrbitalLaser, ReflectorShield,
                       SpaceStation)
from spaceobject import SpaceObject
from stats import Stats
from v2 import V2

import planet


class Building:
    upgrade = None
    def __init__(self):
        self.shapes = []
        self.stats = Stats()

    def load_shapes(self, name):
        data = json.load(open(resource_path("assets/buildings/%s.json" % name)))
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


    def draw_foreground(self, surface, offset, angle, construction=0):
        ind = int((1 - construction / 3) * len(self.shapes))
        for i, (points, color) in enumerate(self.shapes[0:ind]):
            if construction > 0 and i == ind - 1:
                color = PICO_WHITE
            self.draw_shape(surface, points, color, offset, angle)

    def draw_outline(self, surface, color, offset, angle, expand=False, construction=0):
        if construction > 0 and ((construction * 9) % 1) > 0.5:
            color = PICO_WHITE
        for points, _ in self.shapes:
            self.draw_shape(surface, points, color, offset + V2(-1,0), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(+1,0), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(0,-1), angle, expand)
            self.draw_shape(surface, points, color, offset + V2(0,+1), angle, expand)

    def kill(self):
        pass

    def is_alive(self):
        return self.alive()

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
                b = bullet.Bullet(
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
            b = bullet.Bullet(
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
            b = bullet.Bullet(
                planet.pos + V2.from_angle(angle) * planet.get_radius(),
                t, 
                planet, vel=V2.from_angle(angle) * 20, mods={
                        'homing':1, "damage_base":10 * planet.planet_weapon_mul, "blast_radius":10, "color":PICO_WHITE, "life":5, "missile_speed":0.5
                    }
                )
            planet.scene.game_group.add(b)              

# TODO: re-empl with aura, larger radius
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

class OffWorldMiningBuilding(SatelliteBuilding):
    SATELLITE_CLASS = OffWorldMining
    def __init__(self):
        super().__init__()
        self.timer = 0

    def update(self, planet, dt):
        self.timer += dt
        if self.timer >= 5:
            self.timer = self.timer % 5
            planet.owning_civ.earn_resource("iron", 5, where=self.satellite.pos)
            planet.owning_civ.earn_resource("ice", 5, where=self.satellite.pos)
            planet.owning_civ.earn_resource("gas", 5, where=self.satellite.pos)
        return super().update(planet, dt)


class OrbitalLaserBuilding(SatelliteBuilding):
    SATELLITE_CLASS = OrbitalLaser

class AlienHomeDefenseBuilding(Building):
    FIRE_RATE = 2
    THREAT_RANGE = 40
    upgrade = "alienhomedefense"
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("armory")
        self.stats = Stats(planet_health_mul=1)
        self.fire_time = 0
        
    def get_threats(self, planet):
        return planet.scene.get_enemy_ships_in_range(planet.owning_civ, planet.pos, self.THREAT_RANGE + planet.get_radius())

    def update(self, planet, dt):
        # Regenerate
        planet.health += 0.5 * dt
        # Fire at threats
        self.fire_time += dt
        threats = self.get_threats(planet)
        if self.fire_time > self.FIRE_RATE and threats:
            self.fire_time = 0
            threat = random.choice(threats)
            _,angle = (threat.pos - planet.pos).to_polar()
            angle += random.random() * 0.5 - 0.25
            b = bullet.Bullet(
                planet.pos + V2.from_angle(angle) * planet.get_radius(),
                threat, 
                planet, vel=V2.from_angle(angle) * 20, mods={
                    'homing':1,
                    'color':PICO_YELLOW,
                    'damage_base':3,
                    'missile_speed':-0.25,
                    'life':5
                },
                )
            planet.scene.game_group.add(b)

class AuraBuilding(Building):
    def __init__(self):
        super().__init__()
        self.targeting = "enemy"
        self.applied_ships = set()
        self.aura_radius = 80

    def update(self, planet, dt):
        if self.targeting == "enemy":
            ships = set(planet.scene.get_enemy_ships(planet.owning_civ))
        elif self.targeting == "mine":
            ships = set(planet.scene.get_my_ships(planet.owning_civ))
        else:
            ships = set([])
        near = set(all_nearby(planet.pos, ships, self.aura_radius))
        far = ships - near
        for ship in near:
            if ship not in self.applied_ships:
                self.apply(ship, planet)
                self.applied_ships.add(ship)

        for ship in far:
            if ship in self.applied_ships:
                self.unapply(ship, planet)
                self.applied_ships.remove(ship)

        return super().update(planet, dt)     

    def apply(self, ship, planet):
        pass

    def unapply(self, ship, planet):
        pass   

    def kill(self):
        for ship in self.applied_ships:
            self.unapply(ship)
        return super().kill()

class LowOrbitDefensesBuilding(AuraBuilding):
    def __init__(self):
        super().__init__()
        self.targeting = "mine"

    def apply(self, ship, planet):
        ship.bonus_max_health_aura += 20
        ship.health += 20

    def unapply(self, ship, planet):
        ship.bonus_max_health_aura -= 20
        ship.health = min(ship.health, ship.get_max_health())

class ScalingDamageAuraBuilding(AuraBuilding):
    def __init__(self):
        super().__init__()
        self.targeting = "mine"

    def update(self, planet, dt):
        self.aura_radius = 250 - len(planet.buildings) * 25
        return super().update(planet, dt)

    def apply(self, ship, planet):
        ship.add_effect(status_effect.DamageBoostEffect(ship, planet))

    def unapply(self, ship, planet):
        ship.remove_all_effects_by_name("damage_boost")

class DecoyBuilding(AuraBuilding):
    def __init__(self):
        super().__init__()
        self.targeting = "enemy"
        self.aura_radius = 85

    def apply(self, ship, planet):
        if ship.SHIP_BONUS_NAME == "fighter":
            ship.chosen_target = planet
            ship.effective_target = planet
            # Decoy sound effect
            delta = ship.pos - planet.pos
            dn = delta.normalized()
            dist, ang = delta.to_polar()
            t = 0
            p1 = planet.pos
            steps = 8
            for i in range(steps):
                t += 0.25
                
                if i == steps - 1:
                    p2 = ship.pos
                else:
                    p2 = p1 + V2.from_angle(ang + ((i % 2) - 0.5)) * dist / steps
                l = laserparticle.LaserParticle(p1, p2, PICO_BLUE, 0.25 + i / 8)
                planet.scene.game_group.add(l)
                p1 = p2.copy()
        return super().apply(ship, planet)

class UltraBuilding(Building):
    def __init__(self):
        super().__init__()
        self.obj = None

    def kill(self):
        if self.obj:
            self.obj.kill()
        return super().kill()

class DefenseMatrix(UltraBuilding):
    pass

class Portal(Building):
    pass

class CommStationObject(SpaceObject):
    def __init__(self, scene, pos):
        super().__init__(scene, pos)
        self.set_sprite_sheet("assets/commstation.png", 19)
        self.comm_radius = 230

    def update(self, dt):
        return super().update(dt)

class CommStation(UltraBuilding):
    pass


class ReflectorShieldCircleObj(SpaceObject):
    def __init__(self, scene, planet):
        super().__init__(scene, planet.pos)
        self.planet = planet
        self.collidable = True
        self.stationary = False
        self.radius = planet.radius + 7
        self.collision_radius = self.radius
        self._offset = (0.5, 0.5)
        self._generate_image()
        self.health = 50
        self.health_bar.pos = self.pos + V2(0, -planet.radius - 10)

    def bullet_hits(self, bullet):
        return bullet.owning_civ != self.planet.owning_civ

    def get_max_health(self):
        return 50

    def on_die(self):
        self.kill()
        return super().on_die()

    def _generate_image(self):
        r = self.radius + 8
        self._width = r * 2 + 8
        self._height = r * 2 + 8
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        center = V2(r + 4, r + 4)
        pygame.draw.circle(self.image, PICO_PINK, center.tuple(), self.radius, 1)

        self._recalc_rect()


class ReflectorBuilding(Building):
    def __init__(self):
        super().__init__()
        self.shield = None

    def update(self, planet, dt):
        if not self.shield:
            self.shield = ReflectorShieldCircleObj(planet.scene, planet)
            planet.scene.game_group.add(self.shield)
        return super().update(planet, dt)

    def kill(self):
        if self.shield and self.shield.is_alive():
            self.shield.kill()
        return super().kill()
