import math
import random

import asteroid
import planet
import sound
from bullet import Bullet
from colors import *
from helper import all_nearby, clamp, get_nearest
from particle import Particle
from v2 import V2

from ships.all_ships import register_ship

from .ship import (FLEET_RADIUS, STATE_RETURNING, STATE_WAITING,
                   THRUST_PARTICLE_RATE, Ship)

STATE_DOGFIGHT = 'dogfight'
STATE_SIEGE = 'siege'

@register_ship
class Fighter(Ship):
    HEALTHBAR_SIZE = (10,2)
    SHIP_NAME = "fighter"
    SHIP_BONUS_NAME = "fighter"
    FIRE_RATE = 0.75
    BASE_DAMAGE = 4
    BASE_HEALTH = 15

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

        self.post_dogfight_state = None
        self.post_dogfight_target = None
        self.combat_dodge_direction = random.randint(-1,1)

        self.fire_timer = 0
        self._timers['dogfight'] = 0
        self._timers['time'] = 0
        self._timers['opt_threats'] = 0
        self.opt_threats = []

    def get_fire_rate(self):
        rate = self.FIRE_RATE

        if self.get_stat("fire_rate_over_time"):
            rate *= 1 + (self.get_stat("fire_rate_over_time") * min(self._timers['time'] / 60, 1))

        if self.get_stat("overclock"):
            friendly = self.scene.get_my_ships(self.owning_civ)
            # None nearby?
            if not all_nearby(self.pos, friendly, FLEET_RADIUS):
                rate *= 1 + self.get_stat("overclock")

        if self.get_stat("ship_fire_rate_after_takeoff"):
            if self._timers['time'] < 10:
                rate *= 1 + self.get_stat("ship_fire_rate_after_takeoff")

        try:
            rate *= 1 + self.get_stat("%s_fire_rate" % self.SHIP_BONUS_NAME)
        except KeyError:
            pass
        rate *= 1 + self.get_stat("ship_fire_rate")

        rate *= (1 - self.slow_aura)

        if self.bonus_attack_speed_time > 0:
            rate *= 1.67
        return rate

    def get_weapon_range(self):
        range = self.FIRE_RANGE
        range *= (1 + self.get_stat("ship_weapon_range"))
        return range

    def wants_to_land(self):
        return self.state != STATE_DOGFIGHT

    def prepare_bullet_mods(self):
        base_damage = self.BASE_DAMAGE
        if not self.owning_civ.is_enemy and self.SHIP_BONUS_NAME == "fighter":
            fighter_damage_curve = [1, 1.5, 1.9, 2.2]
            base_damage *= fighter_damage_curve[self.scene.game.run_info.ship_levels["fighter"] - 1]
        damage_add = 0
        extra_speed = (self.get_max_speed() - Ship.MAX_SPEED) / Ship.MAX_SPEED
        damage_add += self.get_stat("ship_weapon_damage_speed") * clamp(extra_speed, 0, 1)
        damage_add += self.get_stat("ship_weapon_damage")
        damage_mul = self.get_stat("%s_damage_mul" % self.SHIP_BONUS_NAME)
        mods =  {
            'damage_base': base_damage,
            'damage_mul': damage_mul,
            'damage_add': damage_add,
            'missile_speed':self.get_stat("ship_missile_speed"),
            'raze_upgrade': self.get_stat("raze_upgrade"),
            'color':PICO_LIGHTGRAY,
        }
        if self.SHIP_BONUS_NAME == "fighter":
            mods['iron_on_hit'] = self.get_stat("fighter_damage_iron")
            mods['grey_goo'] = self.get_stat("grey_goo")

        return mods        

    def get_threats(self):
        # OPT - cache results
        if self._timers['opt_threats'] > 0.5:
            self._timers['opt_threats'] = 0
        else:
            return self.opt_threats

        enemies = self.scene.get_enemy_ships_in_range(self.owning_civ, self.pos, self.THREAT_RANGE_DEFAULT * 2)
        enemies.extend(self.scene.get_special_enemies_in_range(self.owning_civ, self.pos, self.THREAT_RANGE_DEFAULT * 2))
        threat_range = self.THREAT_RANGE_DEFAULT
        self.opt_threats = [
            e for e in enemies
            if ((e.pos - self.pos).sqr_magnitude() < threat_range ** 2 and e.is_alive())
        ]
        return self.opt_threats

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

        b = Bullet(self.pos, at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 1.25
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        sound.play(random.choice(['laser1', 'laser2', 'laser3']))

        for i in range(10):
            pvel = (towards + V2((random.random() - 0.5) * 1.5, (random.random()-0.5) * 1.5)).normalized() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 0.2 + random.random() * 0.15, pvel)
            self.scene.game_group.add(p)        

    ### Dogfight ###
    def enter_state_dogfight(self):
        if not self.post_dogfight_state:
            self.post_dogfight_state = self.state
            self.post_dogfight_target = self.effective_target or self.chosen_target
        self.dogfight_initial_pos = self.pos.copy()
        self.find_target()

    def state_dogfight(self, dt):
        def invalid_target():
            return (
                not self.effective_target or
                not self.effective_target.is_alive() or
                (self.effective_target.pos - self.pos).sqr_magnitude() > self.THREAT_RANGE_DEFENSE ** 2 or
                self.effective_target.owning_civ == self.owning_civ
            )
            
        # If our target is dead or w/e, find a new one
        if invalid_target():
            self.find_target()

        if invalid_target(): # Still no target? Go back to whatever we were doing.
            self.set_state(self.post_dogfight_state)
            return

        # Fire if reloaded (and close enough)
        if self.fire_timer > 1:
            if (self.effective_target.pos - self.pos).sqr_magnitude() < self.get_weapon_range() ** 2:
                self.fire_timer = 0
                self.fire(self.effective_target)
                self.target_heading = None

        # Need to get close to the enemy
        delta = self.effective_target.pos - self.pos
        if delta.sqr_magnitude() > self.get_weapon_range() ** 2: # Too far
            dir = delta.normalized()
        elif delta.sqr_magnitude() < (self.get_weapon_range() / 2) ** 2: # Too close
            dir = -delta.normalized()
        elif self.fire_timer > 0.65: # If we're close and about to fire
            dir = delta.normalized()
            self.target_heading = dir.to_polar()[1]
        else:
            _, a = (-delta).to_polar()
            a += self.combat_dodge_direction * 3.14159 / 2
            dir = V2.from_angle(a)           

        # Need to stay close to starting spot
        #delta = self.dogfight_initial_pos - self.pos
        #if delta.sqr_magnitude() > 30 ** 2:
        #    dir = delta.normalized()

        self.target_velocity = dir * self.get_max_speed()

    def get_max_health(self):
        hp = super().get_max_health()
        if not self.owning_civ.is_enemy and self.SHIP_BONUS_NAME == "fighter":
            fighter_hp_curve = [1, 1.3, 1.6, 1.9]
            hp *= fighter_hp_curve[self.scene.game.run_info.ship_levels["fighter"] - 1]        
        return hp

    def exit_state_dogfight(self):
        self.effective_target = self.post_dogfight_target
        self.target_heading = None
        self.post_dogfight_state = None
        self.post_dogfight_target = None

    ### Siege ###
    def state_siege(self, dt):
        if self.DOGFIGHTS and not self.cinematic_no_combat:
            threats = self.get_threats()
            if threats:
                self.set_state(STATE_DOGFIGHT)
                return

        if not self.effective_target or self.effective_target.health <= 0 or self.effective_target.owning_civ == self.owning_civ:
            # If we just killed a planet, stay in waiting.
            if self.effective_target and isinstance(self.effective_target, planet.planet.Planet):
                self.set_state(STATE_WAITING)
            else:
                print("returning from siege")
                self.set_state(STATE_RETURNING)
            return

        tp = self.effective_target.pos + (self.pos - self.effective_target.pos).normalized() * self.effective_target.radius
        delta = tp - self.pos
        dsq_from_target = delta.sqr_magnitude() - self.effective_target.radius ** 2

        def in_range():
            return dsq_from_target <= self.get_weapon_range() ** 2

        # Time to fire and in range?
        if self.fire_timer >= 1:
            if in_range():
                self.fire_timer = 0
                self.fire(self.effective_target)
                if random.random() < 0.33:
                    self.combat_dodge_direction = random.randint(-1,1)
        
        dir = V2(0,0)
        if not in_range():
            dir = delta.normalized()
            self.target_heading = None
        elif self.fire_timer > 0.95:
            dir = delta.normalized()
            self.target_heading = dir.to_polar()[1]
        elif dsq_from_target < (self.get_weapon_range() * 0.66) ** 2:
            dir = -delta.normalized()
            self.target_heading = None
        else:
            _, a = (-delta).to_polar()
            a += self.combat_dodge_direction * 3.14159 / 2
            dir = V2.from_angle(a)
            if self.combat_dodge_direction == 0:
                dir = V2(0,0)             
            self.target_heading = None

        self.target_velocity = dir * self.get_cruise_speed()

    def exit_stage_siege(self):
        self.target_heading = None

    ### Cruising ###
    def state_cruising(self, dt):
        if self.DOGFIGHTS and not self.cinematic_no_combat:
            threats = self.get_threats()
            if threats:
                self.set_state(STATE_DOGFIGHT)
                return

        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, planet.planet.Planet) or isinstance(self.effective_target, asteroid.Asteroid):
            if (delta.sqr_magnitude() - self.effective_target.radius ** 2 - self.get_weapon_range() ** 2) <= 0:
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
        if not self.effective_target.alive():
            self.set_state(STATE_RETURNING)
            
        if self.DOGFIGHTS and not self.cinematic_no_combat:
            threats = self.get_threats()
            if threats:
                self.set_state(STATE_DOGFIGHT)
                return

        # Fixing a bug where sometimes we could be put in waiting but need to get out of it
        if self.BOMBS:
            if isinstance(self.chosen_target, planet.planet.Planet):
                # if enemy planet
                if self.chosen_target.owning_civ and self.chosen_target.owning_civ != self.owning_civ:
                    if self.chosen_target.health > 0:
                        self.effective_target = self.chosen_target
                        self.set_state("cruising") # Cruising, in case we're not close. will go to siege next frame.


        return super().state_waiting(dt)

    def update(self, dt):
        self.fire_timer += self.get_fire_rate() * dt
        return super().update(dt)
