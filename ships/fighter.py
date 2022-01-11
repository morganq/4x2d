import math
import random

import aliens
import asteroid
import helper
import particle
import planet
import pygame
import sound
from bullet import Bullet
from colors import *
from helper import all_nearby, clamp, get_nearest
from particle import Particle

V2 = pygame.math.Vector2

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
    BASE_DAMAGE = 3
    BASE_HEALTH = 15

    FIRE_RANGE = 30
    THREAT_RANGE_DEFAULT = 40
    THREAT_RANGE_DEFENSE = 60
    STOP_CHASING_RANGE = 75

    DOGFIGHTS = True
    BOMBS = True

    FUEL = 250

    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self._set_player_ship_sprite_sheet()
        
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
        self._timers['opt_threats'] = random.random()
        self.opt_threats = []

        self.need_attack_speed_particle = False
        self.attack_speed_particle_angle = 0

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
            if self._timers['time'] < 5:
                rate *= 1 + self.get_stat("ship_fire_rate_after_takeoff")

        try:
            rate *= 1 + self.get_stat("%s_fire_rate" % self.SHIP_BONUS_NAME)
        except KeyError:
            pass
        rate *= 1 + self.get_stat("ship_fire_rate")

        rate *= (1 - self.slow_aura)

        if self.bonus_attack_speed_time > 0:
            rate *= 1.33
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
        extra_speed = (self.get_max_speed() / self.MAX_SPEED) - 1
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
        damage_factor = (mods['damage_mul'] * mods['damage_base'] + mods['damage_add']) / mods['damage_base']
        if damage_factor > 1:
            mods['trail'] = PICO_PINK
            mods['trail_length'] = 0.5 + (damage_factor - 1)
            
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
            if (
                (e.pos - self.pos).length_squared() < threat_range ** 2 and
                e.is_alive() and
                not e.stealth
            )
        ]
        return self.opt_threats

    def find_target(self):
        threats = self.get_threats()
        if threats:
            self.effective_target = random.choice(threats)        
        else:
            self.effective_target = None

    def fire(self, at):
        towards = (at.pos - self.pos).normalize()

        if self.get_stat("ship_take_damage_on_fire"):
            self.health -= self.get_stat("ship_take_damage_on_fire")

        b = Bullet(V2(self.pos), at, self, mods=self.prepare_bullet_mods())
        self.scene.game_group.add(b)

        #self.velocity += -towards * 2
        self.pos += -towards * 1.25
        self.thrust_particle_time = THRUST_PARTICLE_RATE

        sound.play(random.choice(['laser1', 'laser2', 'laser3']))

        for i in range(10):
            pvel = (towards + V2((random.random() - 0.5) * 1.5, (random.random()-0.5) * 1.5)).normalize() * 30 * (random.random() + 0.25)
            p = Particle([PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, V2(self.pos), 0.2 + random.random() * 0.15, pvel)
            self.scene.add_particle(p)   

        self.need_attack_speed_particle = True
        self.attack_speed_particle_angle = towards.as_polar()[1] * 3.14159 / 180
        self.stealth = False

    ### Dogfight ###
    def enter_state_dogfight(self):
        if not self.post_dogfight_state:
            self.post_dogfight_state = self.state
            self.post_dogfight_target = self.effective_target or self.chosen_target
        self.dogfight_initial_pos  = V2(self.pos)
        self.find_target()

    def state_dogfight(self, dt):
        def invalid_target():
            return (
                not self.effective_target or
                not self.effective_target.is_alive() or
                (self.effective_target.pos - self.pos).length_squared() > self.THREAT_RANGE_DEFENSE ** 2 or
                self.effective_target.owning_civ == self.owning_civ
            )
            
        # If our target is dead or w/e, find a new one
        if invalid_target():
            self.find_target()

        if invalid_target(): # Still no target? Go back to whatever we were doing.
            self.set_state(self.post_dogfight_state)
            return

        # If we're defending a planet...
        if self.defending:
            # And our dogfight target is too far...
            if (self.effective_target.pos - self.defending.pos).length_squared() > self.STOP_CHASING_RANGE ** 2:
                self.set_state("returning")

        # Fire if reloaded (and close enough)
        if self.fire_timer > 1:
            if (self.effective_target.pos - self.pos).length_squared() < self.get_weapon_range() ** 2:
                self.fire_timer = 0
                self.fire(self.effective_target)
                self.target_heading = None

        # Need to get close to the enemy
        delta = self.effective_target.pos - self.pos
        if delta.length_squared() > self.get_weapon_range() ** 2: # Too far
            dir = delta.normalize()
        elif delta.length_squared() < (self.get_weapon_range() / 2) ** 2: # Too close
            dir = -delta.normalize()
        elif self.fire_timer > 0.65: # If we're close and about to fire
            dir = delta.normalize()
            self.target_heading = dir.as_polar()[1] * 3.14159 / 180
        else:
            _, a = (-delta).as_polar()
            a *= 3.14159 / 180
            a += self.combat_dodge_direction * 3.14159 / 2
            dir = helper.from_angle(a)           

        # Need to stay close to starting spot
        #delta = self.dogfight_initial_pos - self.pos
        #if delta.length_squared() > 30 ** 2:
        #    dir = delta.normalize()

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

    def wants_to_dogfight(self):
        return self.DOGFIGHTS

    ### Siege ###
    def state_siege(self, dt):
        if self.wants_to_dogfight() and not self.cinematic_no_combat:
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

        tp = self.effective_target.pos + (self.pos - self.effective_target.pos).normalize() * self.effective_target.radius
        delta = tp - self.pos
        dsq_from_target = delta.length_squared() - self.effective_target.radius ** 2

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
            dir = delta.normalize()
            self.target_heading = None
        elif self.fire_timer > 0.95:
            dir = delta.normalize()
            self.target_heading = dir.as_polar()[1] * 3.14159 / 180
        elif dsq_from_target < (self.get_weapon_range() * 0.66) ** 2:
            dir = -delta.normalize()
            self.target_heading = None
        else:
            _, a = (-delta).as_polar()
            a *= 3.14159 / 180
            a += self.combat_dodge_direction * 3.14159 / 2
            dir = helper.from_angle(a)
            if self.combat_dodge_direction == 0:
                dir = V2(0,0)             
            self.target_heading = None

        self.target_velocity = dir * self.get_cruise_speed()

    def exit_stage_siege(self):
        self.target_heading = None

    ### Cruising ###
    def state_cruising(self, dt):
        if self.wants_to_dogfight() and not self.cinematic_no_combat:
            threats = self.get_threats()
            if threats:
                self.set_state(STATE_DOGFIGHT)
                return

        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, (planet.planet.Planet, asteroid.Asteroid, aliens.bossmothership.BossMothership)):
            if (delta.length_squared() - self.effective_target.radius ** 2 - self.get_weapon_range() ** 2) <= 0:
                if self.BOMBS: # If we can attack planets, figure out what to do
                    # If it's an allied mothership, we want to enter waiting and orbit it.
                    if self.effective_target.owning_civ == self.owning_civ and isinstance(self.effective_target, aliens.bossmothership.BossMothership):
                        self.set_state(STATE_WAITING)
                        return
                    # If it's an enemy motherhsip, we want to siege it as if it was a planet.
                    if self.effective_target.owning_civ != self.owning_civ and isinstance(self.effective_target, aliens.bossmothership.BossMothership):
                        self.set_state(STATE_SIEGE)
                        return
                    elif isinstance(self.effective_target, asteroid.Asteroid):
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
            
        if self.wants_to_dogfight() and not self.cinematic_no_combat:
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

    def take_damage(self, damage, origin=None):
        super().take_damage(damage, origin=origin)
        # When we get hit by an enemy, we may want to switch target.
        current_target_dogfights = False
        if isinstance(self.effective_target, Fighter): # Fighter or any subclass
            if self.effective_target.DOGFIGHTS:
                current_target_dogfights = True

        if self.state == STATE_DOGFIGHT and origin:
            shooter = origin
            if hasattr(origin, "shooter"):
                shooter = origin.shooter
            
            if shooter and isinstance(shooter, Ship) and shooter.is_alive() and shooter.owning_civ != self.owning_civ and not current_target_dogfights:
                self.effective_target = shooter


    def update(self, dt):
        if self.need_attack_speed_particle and (self.fire_timer < self.get_fire_rate() / 3) and ((self.fire_timer + dt) >= self.get_fire_rate() / 3):
            self.need_attack_speed_particle = False
            self.make_attack_speed_particle()
        self.fire_timer += self.get_fire_rate() * dt
        
        return super().update(dt)

    def make_attack_speed_particle(self):
        as_factor = self.get_fire_rate() / self.FIRE_RATE
        if as_factor > 1:
            extra = int((as_factor - 1) * 3) + 1
            for i in range(3 + extra):
                ang = self.attack_speed_particle_angle
                ang += (random.random() - 0.5) * 1.6
                pos = self.pos + helper.from_angle(ang) * (4 + random.random() * 3)
                colors = [PICO_BLUE, PICO_WHITE, PICO_GREEN, PICO_PINK, PICO_PURPLE]
                colors = colors[0:extra]                
                p = Particle([random.choice(colors)], 1, pos, 0.1, -helper.from_angle(ang) * 30)
                self.scene.add_particle(p)

    def emit_thrust_particles(self):
        for i in range(2):
            pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
            pvel += -self.velocity / 2
            p = particle.Particle([PICO_YELLOW, PICO_RED, PICO_LIGHTGRAY, PICO_DARKGRAY, PICO_DARKGRAY], 1, self.pos + -self.velocity.normalize() * self.radius, 1, pvel)
            self.scene.add_particle(p)
