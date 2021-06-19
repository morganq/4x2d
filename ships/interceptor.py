from ships.fighter import Fighter, STATE_DOGFIGHT
from ships.ship import Ship, THRUST_PARTICLE_RATE, STATE_WAITING, STATE_CRUISING
from colors import *
from particle import Particle
from v2 import V2
import random
import math
import planet
from helper import all_nearby, clamp
from bullet import Bullet
from ships.bomber import Bomber
import sound

class Interceptor(Fighter): 
    BASE_HEALTH = 50
    BLAST_RADIUS = 7
    FIRE_RATE = 1.0
    BASE_DAMAGE = 5

    FIRE_RANGE = 20
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    BOMBS = False
    DOGFIGHTS = True

    SHIP_NAME = "interceptor"
    SHIP_BONUS_NAME = "interceptor"

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/interceptor.png", 12)
        self.bullets_chambered = 0
        self.fast_fire_timer = 0
        self.firing_target = None

    def get_fire_rate(self):
        r = super().get_fire_rate()
        if self.get_stat("interceptor_fire_rate_deep_space") and self.is_in_deep_space():
            r *= 1 + self.get_stat("interceptor_fire_rate_deep_space")

        if self.get_stat("interceptor_fire_rate_near_bombers") and self.fleet:
            for ship in self.fleet.ships:
                if isinstance(ship, Bomber):
                    r *= 1 + self.get_stat("interceptor_fire_rate_near_bombers")
                    break # Don't double count if there's more bombers!

        return r 

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['bounces'] = self.get_stat("interceptor_missile_bounce")
        mods['color'] = PICO_YELLOW
        return mods

    def special_fire(self, at):
        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(self.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        sound.play(random.choice(['laser1', 'laser2', 'laser3']))

        #self.velocity += -towards * 2
        self.pos += -towards * 1
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)               

        self.bullets_chambered -= 1

    def fire(self, at):
        self.bullets_chambered = 3
        self.firing_target = at
        self.special_fire(at)

    def update(self, dt):
        if self.bullets_chambered > 0:
            self.fast_fire_timer += dt
            if self.fast_fire_timer > 0.15:
                self.fast_fire_timer = 0
                self.special_fire(self.firing_target)
        return super().update(dt)