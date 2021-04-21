from v2 import V2
from colors import *
import pygame
from bullet import Bullet
import random
from stats import Stats
import json

BUILDINGS = {

}

def building(cls):
    BUILDINGS[cls.upgrade] = cls
    return cls

class Building:
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
            new_pt = V2.from_angle(ang) * dist * 2 + offset
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

def make_simple_stats_building(name, stats=None, shape=None):
    class AdHocBuilding(Building):
        upgrade = name
        def __init__(self):
            super().__init__()
            self.load_shapes(shape)
            self.stats = stats

    building(AdHocBuilding)
    return name

@building
class RegenBuilding(Building):
    upgrade = "health2a"
    def __init__(self):
        Building.__init__(self)
        self.load_shapes("repairbay")
        
        
    def update(self, planet, dt):
        planet.health += 1 * dt

@building
class ArmoryBuilding(Building):
    FIRE_RATE = 5
    upgrade = "pop2b"
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
                    planet, vel=V2.from_angle(angle) * 20, mods={'homing':1, "damage_debuff":0.5}
                    )
                planet.scene.game_group.add(b)

@building
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