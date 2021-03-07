from .fighter import Fighter
from colors import *
from bullet import Bullet
from particle import Particle
import random
from .ship import THRUST_PARTICLE_RATE
from v2 import V2

FIRE_RATE = 0.65
FIND_NEW_PLANET_TIME = 9

class AlienBattleship(Fighter):
    HEALTHBAR_SIZE = (24,2)
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-battleship.png", 12)
        self.name = "alien-battleship"
        self.base_health = 70
        self.health = 70
        self.size = 4

    def assault(self, target, dt):
        threats = self.get_threats()
        if threats:
            target = random.choice(threats)
        self.fire_time += dt
        fleet_target_vector = self.get_fleet_target_vector()
        if fleet_target_vector.sqr_magnitude() > 2 ** 2:
            self.state = "traveling"
            self.force_travel_time = 0.125

        towards = (target.pos - self.pos).normalized()
        cross = self.turn_towards(towards, dt)
        rate = FIRE_RATE / (1 + self.owning_civ.get_stat("fire_rate"))
        if abs(cross) < 0.1 and self.fire_time >= rate:
            self.fire_time = 0
            b = Bullet(self.pos, target, self, {})
            self.scene.game_group.add(b)

            self.velocity += -towards * 1
            #self.pos += -towards * 1
            self.thrust_particle_time = THRUST_PARTICLE_RATE

            for i in range(10):
                pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
                p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos + towards * 4, 0.2 + random.random() * 0.15, pvel)
                self.scene.game_group.add(p)

    def update(self, dt):
        if self.bad_target_timer > FIND_NEW_PLANET_TIME:
            self.target = random.choice(self.scene.get_planets())
            self.bad_target_timer = 0
        return super().update(dt)