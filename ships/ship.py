from colors import PICO_DARKGRAY, PICO_PINK, PICO_WHITE
from v2 import V2
from spaceobject import SpaceObject
import random
import math
import particle
import bullet
import helper

FLEET_RADIUS = 15

TARGET_POWER = 4
FLEET_HEADING_POWER = 1
FLEET_SEPARATION_POWER = 1
FLEET_SEPARATION_DEGRADE = 100
FLEET_SEPARATION_MAX = 12
FLEET_PROXIMITY_POWER = 1
WARP_DRIVE_TIME = 30.0
WARP_PLANET_MIN_DIST = 15

BASE_HEALTH = 10

THRUST_PARTICLE_RATE = 0.25

# Particle effects

class Ship(SpaceObject):
    HEALTHBAR_SIZE = (14,2)
    def __init__(self, scene, pos, owning_civ):
        SpaceObject.__init__(self, scene, pos)
        self.base_speed = 7
        self.target = None        
        self.velocity = V2(0,0)
        self.push_velocity = V2(0,0)
        self.orbits = True
        
        self.collidable = True
        self.collision_radius = 1

        self.thrust_particle_time = 0        

        self.warp_drive_countdown = 0
        self.warp_drive_t = 0
        self.base_health = BASE_HEALTH                
        self.owning_civ = owning_civ
        self.offset = (0.5,0.5)
        self.speed_t = random.random() * 6.2818
        self._layer = 2

        self._recalc_rect()
        self.set_health(self.get_max_health())

    def get_max_health(self):
        return self.base_health * (1 + self.owning_civ.get_stat('ship_health'))

    def update(self, dt):
        self.health_bar.pos = self.pos + V2(0, -self.height / 2)
        if self.health <= 0:
            self.kill()        

        self.warp_drive_countdown -= dt

        self.push_from_planets(dt)
        super().update(dt)

    def push_from_planets(self,dt):
        for planet in self.scene.get_planets():
            dist = (planet.pos - self.pos).sqr_magnitude()
            if dist < (planet.get_radius() + 5) ** 2:
                delta = (self.pos - planet.pos)
                dir = delta.normalized()
                mag = abs((planet.get_radius() + 5) - delta.magnitude())
                fwd = V2.from_angle(self._angle)
                self.push_velocity = dir * mag
                w = fwd.cross(dir)
                if w > 0:
                    self._angle += 5 * dt
                    self.push_velocity += V2(dir.y, -dir.x) * 2
                else:
                    self._angle -= 5 * dt
                    self.push_velocity -= V2(dir.y, -dir.x) * 2
        self.push_velocity *= 0.9
                

    def default_update(self, dt):
        self.travel_to_target(dt)
        self._update_image()

    def can_land(self, p):
        return p.owning_civ == self.owning_civ and p == self.target

    def turn_towards(self, vector, dt):
        facing = V2.from_angle(self._angle)
        cp = facing.cross(vector)
        try:
            ao = math.acos(facing.dot(vector))
        except ValueError:
            ao = 0
        if ao < 0.25:
            self._angle = math.atan2(vector.y, vector.x)
        else:
            if cp > 0:
                self._angle += 3 * dt
            else:
                self._angle -= 3 * dt
        return cp

    def try_warp(self, dt):
        if self.owning_civ.get_stat('warp_drive') == 0:
            return
        if self.warp_drive_countdown > 0:
            return

        towards = (self.target.pos - self.pos).normalized()
        nearest,dist = helper.get_nearest(self.pos, self.scene.get_planets())
        if nearest:
            if dist < (nearest.get_radius() + WARP_PLANET_MIN_DIST) ** 2:
                return

        if self.warp_drive_t < 0.66:
            self.velocity = V2(0,0)
            self.warp_drive_t += dt
            if int(self.warp_drive_t * 40) % 2 == 0:
                pvel = V2(random.random() - 0.5, random.random() - 0.5) * 15
                pvel -= towards * 25
                p = particle.Particle([PICO_WHITE, PICO_PINK],1,self.pos,0.25 + random.random() * 0.25,pvel)
                self.scene.game_group.add(p)
            return

        exit_dist = (self.target.pos - self.pos).magnitude() - self.target.get_radius() - WARP_PLANET_MIN_DIST

        max_dist = self.owning_civ.get_stat('warp_drive') + 30
        dist = min(exit_dist, max_dist)

        print(dist)


        for i in range(0, int(dist), 4):
            p = self.pos + towards * i
            pvel = V2(random.random() - 0.5, random.random() - 0.5) * 15
            pvel += towards * 15
            p = particle.Particle([PICO_WHITE, PICO_PINK],1,p,0.25 + random.random() * 0.5,pvel)
            self.scene.game_group.add(p)
            nearest,d = helper.get_nearest(p, self.scene.get_planets())
            if nearest and d < (nearest.get_radius() + WARP_PLANET_MIN_DIST) ** 2:
                dist = i
                break


        self.warp_drive_t = 0

        self.pos = self.pos + towards * dist
        print(towards, dist, self.pos)
        self.warp_drive_countdown = WARP_DRIVE_TIME * (dist / max_dist)

    def travel_to_target(self, dt):
        ### Directional Forces ###
        target_vector = V2(0,0)

        # Towards target
        if self.orbits:
            orbital_pos = (self.pos - self.target.pos).normalized() * (self.target.radius + 20) + self.target.pos
            towards_angle = (orbital_pos - self.pos).to_polar()[1]
        else:
            towards_angle = (self.target.pos - self.pos).to_polar()[1]
        towards_angle += math.sin(self.speed_t) / 4
        target_vector += V2.from_angle(towards_angle) * TARGET_POWER

        target_vector += self.get_fleet_target_vector()

        # Now turn towards that target vector
        target_vector = target_vector.normalized()
        self.turn_towards(target_vector, dt)

        self.speed_t += dt
        speed = math.sin(self.speed_t) * 2 + self.base_speed
        self.velocity = V2.from_angle(self._angle) * speed

        self.try_warp(dt)            

        self.pos += (self.velocity + self.push_velocity) * dt

        if self.velocity.sqr_magnitude() > 0:
            self.thrust_particle_time += dt
            if self.thrust_particle_time > THRUST_PARTICLE_RATE:
                pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
                pvel += -self.velocity / 2
                p = particle.Particle("assets/thrustparticle.png",1,self.pos + -self.velocity.normalized() * self.radius,1,pvel)
                self.scene.game_group.add(p)
                self.thrust_particle_time -= THRUST_PARTICLE_RATE

    def get_fleet_target_vector(self):
        target_vector = V2(0,0)
        our_ships = self.scene.get_civ_ships(self.owning_civ)
        fleet_ships = [s for s in our_ships if (s.pos - self.pos).sqr_magnitude() <= FLEET_RADIUS ** 2]
        fleet_ships.remove(self)

        # Separation
        for ship in fleet_ships:
            delta = ship.pos - self.pos
            sm = delta.sqr_magnitude()
            if sm < FLEET_SEPARATION_MAX ** 2:
                target_vector -= (delta.normalized() * (FLEET_SEPARATION_DEGRADE / sm)) * FLEET_SEPARATION_POWER

        # Proximity
        center = V2(0,0)
        for ship in fleet_ships:
            center += ship.pos / len(fleet_ships)

        delta = center - self.pos
        target_vector += delta.normalized() * FLEET_PROXIMITY_POWER

        return target_vector

    def kill(self):
        self.health_bar.kill()
        super().kill()