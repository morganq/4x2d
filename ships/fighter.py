from colors import PICO_BLUE, PICO_DARKBLUE, PICO_WHITE
from particle import Particle
from .ship import Ship, THRUST_PARTICLE_RATE
from bullet import Bullet
import random
from v2 import V2

RANGE = 21

FIRE_RATE = 1.0

class Fighter(Ship):
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ, "assets/fighter.png")
        self.collision_radius = 4
        self.state = "traveling"

        self.fire_time = 0
        self.force_travel_time = 0

    def assault(self, dt):
        self.fire_time += dt
        fleet_target_vector = self.get_fleet_target_vector()
        if fleet_target_vector.sqr_magnitude() > 2 ** 2:
            self.state = "traveling"
            self.force_travel_time = 1.0

        towards = (self.target.pos - self.pos).normalized()
        cross = self.turn_towards(towards, dt)
        rate = FIRE_RATE / (1 + self.owning_civ.upgrade_stats['fire_rate'])
        if abs(cross) < 0.1 and self.fire_time >= rate:
            self.fire_time = 0
            b = Bullet(self.pos, self.target, self, {})
            self.scene.game_group.add(b)

            self.velocity += -towards * 2
            self.pos += -towards * 2
            self.thrust_particle_time = THRUST_PARTICLE_RATE

            for i in range(10):
                pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
                p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
                self.scene.game_group.add(p)

    def is_assault_target(self, t):
        return t.owning_civ != None and t.owning_civ != self.owning_civ

    def collide(self, other):
        if self.can_land(other):
            self.kill()
            other.add_ship("fighter")

    def update(self, dt):
        delta = (self.target.pos - self.pos)
        in_range = delta.sqr_magnitude() < (RANGE + self.target.collision_radius) ** 2
        if self.is_assault_target(self.target) and in_range:
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
            self.assault(dt)
            self.pos += self.velocity * dt

        self._update_image()            