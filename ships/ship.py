from v2 import V2
from animrotsprite import AnimRotSprite
import random
import math
import particle
import bullet

FLEET_RADIUS = 15

TARGET_POWER = 4
FLEET_HEADING_POWER = 1
FLEET_SEPARATION_POWER = 1
FLEET_SEPARATION_DEGRADE = 100
FLEET_SEPARATION_MAX = 12
FLEET_PROXIMITY_POWER = 1

THRUST_PARTICLE_RATE = 0.25

# Particle effects

class Ship(AnimRotSprite):
    def __init__(self, scene, pos, owning_civ, sheet):
        AnimRotSprite.__init__(self, pos, sheet, 12)
        self.base_speed = 7
        self.scene = scene
        self.owning_civ = owning_civ
        self.target = None
        self.offset = (0.5,0.5)
        self.speed_t = random.random() * 6.2818
        self._layer = 2
        self.velocity = V2(0,0)
        self.orbits = True

        self.collidable = True
        self.collision_radius = 1

        self.thrust_particle_time = 0
        self._recalc_rect()

    def update(self, dt):
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

    def travel_to_target(self, dt):
        ### Directional Forces ###
        target_vector = V2(0,0)

        # Towards target
        if self.orbits:
            orbital_pos = (self.pos - self.target.pos).normalized() * (self.target.size + 20) + self.target.pos
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
        self.pos += self.velocity * dt

        self.thrust_particle_time += dt
        if self.thrust_particle_time > THRUST_PARTICLE_RATE:
            pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
            pvel += -self.velocity / 2
            p = particle.Particle("assets/thrustparticle.png",1,self.pos,1,pvel)
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