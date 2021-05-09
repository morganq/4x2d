from helper import all_nearby, clamp, get_nearest
from colors import PICO_BLUE, PICO_DARKBLUE, PICO_WHITE
from particle import Particle
from .ship import FLEET_RADIUS, STATE_RETURNING, STATE_WAITING, Ship, THRUST_PARTICLE_RATE
from bullet import Bullet
from planet import planet
import asteroid
import random
import math
from v2 import V2



STATE_DOGFIGHT = 'dogfight'
STATE_SIEGE = 'siege'

class Fighter(Ship):
    HEALTHBAR_SIZE = (10,2)
    SHIP_NAME = "fighter"
    FIRE_RATE = 0.75
    BASE_DAMAGE = 5

    FIRE_RANGE = 30
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60

    DOGFIGHTS = True
    BOMBS = True

    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/fighter.png", 12)
        self.states[STATE_DOGFIGHT] = {
            'update':self.state_dogfight,
            'enter':self.enter_state_dogfight,
            'exit':self.exit_state_dogfight
        }
        self.states[STATE_SIEGE] = {
            'update':self.state_siege,
            'exit':self.exit_stage_siege
        }
        self._timers['gun'] = 0
        self._timers['dogfight'] = 0

    def get_fire_rate(self):
        rate = self.FIRE_RATE
        if self.get_stat("overclock"):
            friendly = self.scene.get_my_ships(self.owning_civ)
            # None nearby?
            if not all_nearby(self.pos, friendly, FLEET_RADIUS):
                rate *= 1 + self.get_stat("overclock")

        try:
            rate *= 1 + self.get_stat("%s_fire_rate" % self.SHIP_NAME)
        except KeyError:
            pass
        rate *= 1 + self.get_stat("ship_fire_rate")
            
        return rate

    def get_max_health(self):
        return self.BASE_HEALTH * (
            self.get_stat("ship_health_mul") + self.get_stat("fighter_health_mul") + 1
        ) + self.get_stat("ship_health_add") + self.get_stat("fighter_health_add")

    def get_weapon_range(self):
        range = self.FIRE_RANGE
        range *= (1 + self.get_stat("ship_weapon_range"))
        return range

    def wants_to_land(self):
        return self.state != STATE_DOGFIGHT

    def get_threats(self):
        enemies = self.scene.get_enemy_ships(self.owning_civ)
        threat_range = self.THREAT_RANGE_DEFAULT
        if self.chosen_target.owning_civ == self.owning_civ: # Target is our own planet (defense)
            threat_range = self.THREAT_RANGE_DEFENSE
        return [
            e for e in enemies
            if ((e.pos - self.pos).sqr_magnitude() < threat_range ** 2 and e.health > 0)
        ]

    def find_target(self):
        threats = self.get_threats()
        if threats:
            self.effective_target = random.choice(threats)        
        else:
            self.effective_target = None

    def fire(self, at):
        towards = (at.pos - self.pos).normalized()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        damage_add = 0
        extra_speed = (self.get_max_speed() - Ship.MAX_SPEED) / Ship.MAX_SPEED
        damage_add += self.get_stat("ship_weapon_damage_speed") * clamp(extra_speed, 0, 1)
        damage_add += self.get_stat("ship_weapon_damage")
        damage_mul = self.get_stat("fighter_damage_mul")
        blast_radius = self.get_stat("fighter_blast_radius")
        b = Bullet(self.pos, at, self, mods={
            'grey_goo': self.get_stat('grey_goo'),
            'damage_base': self.BASE_DAMAGE,
            'damage_mul': damage_mul,
            'damage_add': damage_add,
            'homing': False,
            'blast_radius': blast_radius,
            'ship_missile_speed':self.get_stat("ship_missile_speed")
        })
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 2
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        for i in range(10):
            pvel = (towards + V2((random.random() - 0.5) * 1.5, (random.random()-0.5) * 1.5)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)        

    ### Dogfight ###
    def enter_state_dogfight(self):
        self.post_dogfight_state = self.state
        self.post_dogfight_target = self.effective_target or self.chosen_target
        self.dogfight_initial_pos = self.pos.copy()
        self.find_target()
        self._timers['gun'] = 0

    def state_dogfight(self, dt):
        # If our target is dead or w/e, find a new one
        if (not self.effective_target or
            self.effective_target.health <= 0 or
            (self.effective_target.pos - self.pos).sqr_magnitude() > self.THREAT_RANGE_DEFENSE ** 2):
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
        self.target_heading = None

    ### Siege ###
    def state_siege(self, dt):
        threats = self.get_threats()
        if threats:
            self.set_state(STATE_DOGFIGHT)
            return

        if not self.effective_target or self.effective_target.health <= 0 or self.effective_target.owning_civ == self.owning_civ:
            # If we just killed a planet, stay in waiting.
            if self.effective_target and isinstance(self.effective_target, planet.Planet):
                self.set_state(STATE_WAITING)
            else:
                self.path = None
                self.set_state(STATE_RETURNING)
            return

        delta = self.effective_target.pos - self.pos
        # In range?
        if delta.magnitude() - self.effective_target.radius <= self.get_weapon_range():
            rate = self.get_fire_rate()
            if self._timers['gun'] >= 1 / rate:
                self._timers['gun'] = self._timers['gun'] % (1 / rate)
                self.fire(self.effective_target)
            self.target_heading = delta.to_polar()[1]
        else: # Out of range? head towards.
            self.target_heading = None
        
        tp = (self.pos - self.effective_target.pos).normalized() * (self.effective_target.radius + self.get_weapon_range() * 0.5) + self.effective_target.pos
        delta = tp - self.pos
        if delta.sqr_magnitude() > 5 ** 2:
            self.target_velocity = delta.normalized() * self.get_cruise_speed()
        else:
            self.target_velocity = V2(0,0)

    def exit_stage_siege(self):
        self.target_heading = None

    ### Cruising ###
    def state_cruising(self, dt):
        if self.DOGFIGHTS:
            threats = self.get_threats()
            if threats:
                self.set_state(STATE_DOGFIGHT)
                return

        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, planet.Planet) or isinstance(self.effective_target, asteroid.Asteroid):
            if (delta.magnitude() - self.effective_target.radius - self.get_weapon_range()) <= 0:
                if self.BOMBS: # If we can attack planets, figure out what to do
                    if isinstance(self.effective_target, asteroid.Asteroid):
                        self.set_state(STATE_SIEGE)
                        return
                    elif not self.effective_target.owning_civ or self.effective_target.health <= 0:
                        self.set_state(STATE_WAITING)
                        return
                    elif self.effective_target.owning_civ != self.owning_civ:
                        self.set_state(STATE_SIEGE)
                        return
                else: # If we can't, we just go into WAITING unless its our planet
                    if self.effective_target.owning_civ != self.owning_civ:
                        self.set_state(STATE_WAITING)
                        return

                            
        return super().state_cruising(dt)

    ### Waiting ###
    def state_waiting(self, dt):
        threats = self.get_threats()
        if threats:
            self.set_state(STATE_DOGFIGHT)
            return
        return super().state_waiting(dt)