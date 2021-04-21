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

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        
        self.set_sprite_sheet("assets/interceptor.png", 12)
        self.bullets_chambered = 0

    def get_fire_rate(self):
        r = super().get_fire_rate()
        if self.get_stat("interceptor_fire_rate_deep_space") and self.is_in_deep_space():
            r *= 1 + self.get_stat("interceptor_fire_rate_deep_space")
        return r 

    def fire(self, at):
        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        damage_add = 0
        extra_speed = (self.get_max_speed() - Ship.MAX_SPEED) / Ship.MAX_SPEED
        damage_add += self.get_stat("ship_weapon_damage_speed") * clamp(extra_speed, 0, 1)
        damage_add += self.get_stat("ship_weapon_damage")
        damage_mul = self.get_stat("interceptor_damage_mul")
        blast_radius = self.BLAST_RADIUS + self.get_stat("interceptor_blast_radius")
        b = Bullet(self.pos, at, self, mods={
            'grey_goo': self.get_stat('grey_goo'),
            'damage_base': self.BASE_DAMAGE,
            'damage_mul': damage_mul,
            'damage_add': damage_add,
            'blast_radius': blast_radius,
            'ship_missile_speed':self.get_stat("ship_missile_speed"),
            'bounces':self.get_stat("interceptor_missile_bounce"),
            'color':PICO_YELLOW,
        })
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 1
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)               

        self.bullets_chambered -= 1

    def state_dogfight(self, dt):
        # If our target is dead or w/e, find a new one
        if not self.effective_target or self.effective_target.health <= 0:
            self.find_target()

        if not self.effective_target: # Still no target? Go back to whatever we were doing.
            self.set_state(self.post_dogfight_state)
            return

        # Swoop towards and away
        rate = self.get_fire_rate()
        gt = self._timers['dogfight'] * rate
        t = math.cos(gt * 6.2818 + 3.14159) * -0.5 + 0.5
        if self._timers['gun'] >= 1 / rate:
            if (self.effective_target.pos - self.pos).sqr_magnitude() < self.get_weapon_range() ** 2:
                self.bullets_chambered = 3
                self._timers['gun'] = self._timers['gun'] % (1 / rate)

        fire_tick = ((self._timers['gun'] * 6) % 1) < (((self._timers['gun'] - dt) * 6) % 1)
        if self.bullets_chambered > 0 and fire_tick:
            nearby = all_nearby(self.pos, self.get_threats(), self.FIRE_RANGE * 1.5)
            if nearby:
                self.fire(random.choice(nearby))

        t2 = math.cos(gt * 3.14159)
        
        vtowards = (self.effective_target.pos - self.pos).normalized()
        vside = (V2(vtowards.y, -vtowards.x) * t2).normalized()

        if t > 0.5:
            dir = vtowards
            self.target_heading = vtowards.to_polar()[1]
        else:
            dir = vside
        #dir = vtowards * t + vside * (1-t)
        # Hacky stufffff
        if (self.effective_target.pos - self.pos).sqr_magnitude() < 10 ** 2:
            dir = -vtowards

        # dist to starting spot
        delta = self.dogfight_initial_pos - self.pos
        if delta.sqr_magnitude() > 30 ** 2:
            dir = delta.normalized()

        self.target_velocity = dir * self.get_max_speed()        