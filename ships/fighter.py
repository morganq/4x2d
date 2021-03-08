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

STATE_DOGFIGHT = 'dogfight'

class Fighter(Ship):
    HEALTHBAR_SIZE = (10,2)
    SHIP_NAME = "fighter"

    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/fighter.png", 12)
        self.states[STATE_DOGFIGHT] = {
            'update':self.state_dogfight,
            'enter':self.enter_state_dogfight,
            'exit':self.exit_state_dogfight
        }
        self._timers['gun'] = 0
        self._timers['dogfight'] = 0

    def wants_to_land(self):
        return self.state != STATE_DOGFIGHT

    def get_threats(self):
        enemies = self.scene.get_enemy_ships(self.owning_civ)
        threat_range = THREAT_RANGE_DEFAULT
        if self.chosen_target.owning_civ == self.owning_civ:
            threat_range = THREAT_RANGE_DEFENSE
        return [e for e in enemies if (e.pos - self.pos).sqr_magnitude() < threat_range ** 2]        

    def find_target(self):
        threats = self.get_threats()
        if threats:
            self.effective_target = random.choice(threats)        
        else:
            self.effective_target = None

    def fire(self, at):
        towards = (at.pos - self.pos).normalized()
        b = Bullet(self.pos, at, self, {})
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2(random.random() * 0.75, random.random() * 0.75)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)        

    ### Dogfighting ###

    def enter_state_dogfight(self):
        self.post_dogfight_state = self.state
        self.post_dogfight_target = self.effective_target
        self.dogfight_initial_pos = self.pos.copy()
        self.find_target()
        self._timers['gun'] = 0

    def state_dogfight(self, dt):
        # If our target is dead or w/e, find a new one
        if not self.effective_target or self.effective_target.health <= 0:
            self.find_target()

        if not self.effective_target: # Still no target? Go back to whatever we were doing.
            self.set_state(self.post_dogfight_state)
            return

        # Swoop towards and away
        rate = 1 / 3
        gt = self._timers['dogfight'] * rate
        t = math.cos(gt * 6.2818 + 3.14159) * -0.5 + 0.5
        if self._timers['gun'] >= 1 / rate:
            self._timers['gun'] = self._timers['gun'] % (1 / rate)
            self.fire(self.effective_target)
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

    def exit_state_dogfight(self):
        self.effective_target = self.post_dogfight_target

    def state_cruising(self, dt):
        threats = self.get_threats()
        if threats:
            self.set_state(STATE_DOGFIGHT)
            return
        return super().state_cruising(dt)

    def state_waiting(self, dt):
        threats = self.get_threats()
        if threats:
            self.set_state(STATE_DOGFIGHT)
            return
        return super().state_waiting(dt)