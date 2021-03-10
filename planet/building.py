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
        center = offset
        for pt in shape:
            center += pt * (1 / len(shape))
        final_pts = []
        for pt in shape:
            dist,ang = pt.to_polar()
            ang += angle
            new_pt = V2.from_angle(ang) * dist + offset
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

@building
class MiningRateBuilding(Building):
    upgrade = "mining_rate"
    def __init__(self):
        Building.__init__(self)
        self.shapes = [
            ([V2(-1,-3), V2(6,-3), V2(6,0), V2(3,0), V2(3,3), V2(-1,3)], PICO_GREYPURPLE),
            ([V2(-1,-3), V2(0,-3), V2(0,3), V2(-1,3)], PICO_LIGHTGRAY)
        ]
        self.load_shapes("test")
        self.stats = Stats(top_mining_rate = 0.15)

@building
class RegenBuilding(Building):
    upgrade = "regen"
    def __init__(self):
        Building.__init__(self)
        self.shapes = [
            ([V2(-1,-4), V2(2,-2), V2(5,0), V2(2,2), V2(-1,4)], PICO_BLUE),
            ([V2(-1,-4), V2(0,-4), V2(0,4), V2(-1,4)], PICO_LIGHTGRAY)
        ]        
        
        
    def update(self, planet, dt):
        planet.health += 1 * dt

@building
class ArmoryBuilding(Building):
    FIRE_RATE = 5
    upgrade = "armory"
    def __init__(self):
        Building.__init__(self)
        self.shapes = [
            ([V2(-1,-1), V2(2,-1), V2(2,-4), V2(4,-4), V2(4,4), V2(2,4), V2(2,1), V2(-1,1)], PICO_PINK),
            ([V2(-1,-1), V2(0,-2), V2(0,1), V2(-1,1)], PICO_LIGHTGRAY)
        ]        
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
                    planet, vel=V2.from_angle(angle) * 20, mods={'homing':True, "damage_debuff":0.5}
                    )
                planet.scene.game_group.add(b)