from helper import get_nearest
from colors import PICO_BLUE, PICO_DARKBLUE, PICO_WHITE
from particle import Particle
from .ship import Ship, THRUST_PARTICLE_RATE
from bullet import Bullet
import random
import math
from v2 import V2

RANGE = 21
NEARBY_RANGE = 30
FIRE_RATE = 1.0
THREAT_RANGE_DEFAULT = 30
THREAT_RANGE_DEFENSE = 60

BAD_TARGET_FIND_NEW_TIME = 10.0

class Fighter(Ship):
    HEALTHBAR_SIZE = (12,2)
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/fighter.png", 12)
        self.collision_radius = 4
        self.state = "traveling"
        self.name = "fighter"

        self.fire_time = 0
        self.force_travel_time = 0

        self.bad_target_timer = 0
        self.bad_target = False

        self.current_dogfight_target = None

    def assault(self, target, dt):
        self.fire_time += dt
        fleet_target_vector = self.get_fleet_target_vector()
        if fleet_target_vector.sqr_magnitude() > 2 ** 2:
            self.state = "traveling"
            self.force_travel_time = 1.0

        towards = (target.pos - self.pos).normalized()
        cross = self.turn_towards(towards, dt)
        rate = FIRE_RATE / (1 + self.owning_civ.get_stat('fire_rate'))
        if abs(cross) < 0.1 and self.fire_time >= rate:
            self.fire_time = 0
            b = Bullet(self.pos, target, self, {})
            self.scene.game_group.add(b)

            self.velocity += -towards * 2
            self.pos += -towards * 2
            self.thrust_particle_time = THRUST_PARTICLE_RATE

            for i in range(10):
                pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
                p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
                self.scene.game_group.add(p)

    def is_assault_target(self, t):
        return t.owning_civ != None and t.owning_civ != self.owning_civ and t.health > 0

    def is_good_target(self, t):
        return self.is_assault_target(t) or t.owning_civ == self.owning_civ

    def get_threats(self):
        enemies = self.scene.get_enemy_ships(self.owning_civ)
        threat_range = THREAT_RANGE_DEFAULT
        if self.target.owning_civ == self.owning_civ:
            threat_range = THREAT_RANGE_DEFENSE
        return [e for e in enemies if (e.pos - self.pos).sqr_magnitude() < threat_range ** 2]

    def dogfight(self, threats, dt):
        if self.current_dogfight_target == None or self.current_dogfight_target.health <= 0:
            self.current_dogfight_target = random.choice(threats)
        dist = (self.current_dogfight_target.pos - self.pos).sqr_magnitude()
        if dist < RANGE ** 2:
            self.assault(self.current_dogfight_target, dt)
        else:
            towards = (self.current_dogfight_target.pos - self.pos).normalized()
            target_vector = towards
            target_vector += self.get_fleet_target_vector()            
            target_vector = target_vector.normalized()
            self.turn_towards(target_vector, dt)
            self.speed_t += dt
            speed = math.sin(self.speed_t) * 2 + self.base_speed
            self.velocity = V2.from_angle(self._angle) * speed

            self.thrust_particle_time += dt
            if self.thrust_particle_time > THRUST_PARTICLE_RATE:
                pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
                pvel += -self.velocity / 2
                p = Particle("assets/thrustparticle.png",1,self.pos,1,pvel)
                self.scene.game_group.add(p)
                self.thrust_particle_time -= THRUST_PARTICLE_RATE            

    def collide(self, other):
        if not self.get_threats() and self.can_land(other):
            self.kill()
            other.add_ship(self.name)

    def update(self, dt):
        delta = (self.target.pos - self.pos)
        in_range = delta.sqr_magnitude() < (RANGE + self.target.collision_radius) ** 2
        threats = self.get_threats()
        if threats:
            if self.state == "traveling":
                self.velocity = self.velocity * 0.5            
            self.state = "dogfighting"

        elif self.is_assault_target(self.target) and in_range:
            if self.state == "traveling":
                self.velocity = self.velocity * 0.5
            self.state = "firing"
        else:
            self.state = "traveling"

        self.force_travel_time -= dt

        if self.state == "traveling" or self.force_travel_time > 0:
            if self.can_land(self.target):
                self.orbits = False
            else:
                self.orbits = True
            self.travel_to_target(dt)

        elif self.state == "firing":
            self.assault(self.target, dt)
            self.pos += (self.velocity + self.push_velocity) * dt

        elif self.state == "dogfighting":
            self.dogfight(threats, dt)
            self.pos += (self.velocity + self.push_velocity) * dt

        nearby = delta.sqr_magnitude() < (NEARBY_RANGE + self.target.collision_radius) ** 2

        if (not self.is_good_target(self.target)) and nearby:
            self.bad_target_timer += dt
            if self.bad_target_timer > BAD_TARGET_FIND_NEW_TIME:
                self.bad_target = True
        else:
            self.bad_target_timer = 0

        if self.bad_target:
            dist = 9999999
            for p in self.scene.get_civ_planets(self.owning_civ):
                delta = (p.pos - self.pos).sqr_magnitude()
                if delta < dist:
                    dist = delta
                    self.target = p
            

        self._update_image()       

        return super().update(dt)