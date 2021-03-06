from satellite import ReflectorShieldObj
from colors import *
from v2 import V2
from spaceobject import SpaceObject
import planet
import random
import math
import particle
import bullet
import helper
import explosion
import pygame
import sound
from resources import resource_path
from laserparticle import LaserParticle

ROTATE_SPEED = 6.2818
FLEET_RADIUS = 25
FLEET_POWER = 1.5
FLEET_SEPARATION_POWER = 2
FLEET_SEPARATION_DEGRADE = 50
FLEET_SEPARATION_MAX = 12
FLEET_PROXIMITY_POWER = 0.5
ATMO_DISTANCE = 15
WARP_PLANET_MIN_DIST = 15
DEEP_SPACE_DIST = 40
FAR_FROM_HOME_DIST = 100

THRUST_PARTICLE_RATE = 0.25

PATH_FOLLOW_CLOSENESS = 20

STATE_CRUISING = 'cruising'
STATE_RETURNING = 'returning'
STATE_WAITING = 'waiting'
STATE_STUNNED = 'stunned'

class Ship(SpaceObject):
    HEALTHBAR_SIZE = (14,2)
    THRUST_ACCEL = 5
    MAX_SPEED = 8
    BASE_HEALTH = 20
    WARP_DRIVE_TIME = 30.0
    SHIP_NAME = None
    SHIP_BONUS_NAME = None

    def __init__(self, scene, pos, owning_civ):
        SpaceObject.__init__(self, scene, pos)
        self.owning_civ = owning_civ
        self.offset = (0.5, 0.5)
        self.collidable = True
        self.stationary = False
        self.fleet = None

        self._layer = 1

        # States
        self.states = {
            STATE_CRUISING:{'update':self.state_cruising, 'enter':self.enter_state_cruising},
            STATE_WAITING:{'update':self.state_waiting, 'exit':self.exit_state_waiting},
            STATE_RETURNING:{'update':self.state_returning, 'enter':self.enter_state_returning},
            STATE_STUNNED:{'update':self.state_stunned, 'enter':self.enter_state_stunned, 'exit':self.exit_state_stunned}
        }
        self.state = None

        # Movement vars
        self.chosen_target = None
        self.effective_target = None
        self.velocity = V2(0,0)
        self.target_velocity = V2(0,0)
        self.target_heading = None # An angle, or None.
        self.fleet_forces = V2(0,0)
        self.fleet_minimum_forces = 0 # The magnitude of the fleet forces before we start caring

        # Other stuff
        self.time = 0
        self.waiting_time = 0
        self._timers["movement_variation"] = random.random() * 6.2818
        self._timers['thrust_particle_time'] = 0
        self._timers['staged_booster'] = -self.get_stat("staged_booster_time")
        self._timers['stun_time'] = 0
        self._timers['warp_drive'] = 0

        # Upgrades
        self.bonus_max_health_aura = 0
        self.bonus_attack_speed_time = 0
        self.slow_aura = 0

        # Alien stuff
        self.tether_target = False

        # Stuff that has to come at the end
        self.set_health(self.get_max_health())
        self.set_state(STATE_CRUISING)

        # opt
        self._timers['opt_time'] = random.random()
        self.opt_fleet_forces = V2(0,0)

    def get_stat(self, stat):
        return self.owning_civ.get_stat(stat)

    def take_damage(self, damage, origin=None):
        armor = 0
        if self.get_stat("ship_armor_far_from_home"):
            nearest, dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
            if dist > FAR_FROM_HOME_DIST ** 2:
                armor = self.get_stat("ship_armor_far_from_home")
        if damage > 1 and armor > 0:
            damage = max(damage - armor,1)
        
        return super().take_damage(damage, origin=origin)

    def get_thrust_accel(self):
        accel = self.THRUST_ACCEL
        if self._timers['staged_booster'] < 0:
            accel *= 3
        accel *= (1 - self.slow_aura)
        return accel

    def is_target_enemy(self):
        return self.effective_target and self.effective_target.owning_civ and self.effective_target.owning_civ != self.owning_civ

    def is_in_deep_space(self):
        nearest, distsq = helper.get_nearest(self.pos, self.scene.get_planets())
        return distsq > DEEP_SPACE_DIST ** 2

    def get_max_speed(self):
        speed = self.MAX_SPEED
        if self.get_stat("deep_space_drive") and self.is_in_deep_space():
            speed *= (1 + self.get_stat("deep_space_drive"))
            if random.random() < 0.02:
                p = particle.Particle([PICO_WHITE, PICO_GREEN, PICO_GREEN, PICO_DARKGREEN], 1, self.pos, 1.0, self.velocity * -1 + V2.random_angle() * 2)
                self.scene.game_group.add(p)
        if self._timers['staged_booster'] < 0:
            speed *= 2
        if self.get_stat('ship_speed_mul_targeting_planets') and self.is_target_enemy() and isinstance(self.effective_target, planet.planet.Planet):
            speed *= (1 + self.get_stat('ship_speed_mul_targeting_planets'))
            if random.random() < 0.02:
                p = particle.Particle([PICO_WHITE, PICO_BLUE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 1.5, self.velocity * -1 + V2.random_angle() * 1.25)
                self.scene.game_group.add(p)    

        speed *= (1 + self.get_stat("ship_speed_mul"))
        speed *= (1 - self.slow_aura)
        return speed

    def get_cruise_speed(self): return self.get_max_speed() * 0.80

    def get_max_health(self):
        mhp = self.BASE_HEALTH * (self.get_stat("ship_health_mul") + 1) + self.get_stat("ship_health_add") + self.bonus_max_health_aura
        return mhp

    def get_max_shield(self):
        shield = 0
        if self.get_stat("enclosure_shield") and self.fleet and len(self.fleet.ships) >= 8:
            shield += self.get_stat("enclosure_shield")
        if self.get_stat('ship_shield_far_from_home'):
            _, near_dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
            if near_dist > FAR_FROM_HOME_DIST ** 2:
                shield += self.get_stat('ship_shield_far_from_home')
        return shield 

    def wants_to_land(self):
        return True

    def set_target(self, target):
        self.chosen_target = target
        self.effective_target = target

    def can_land(self, target):
        return (
            isinstance(target, planet.planet.Planet) and
            target.owning_civ == self.owning_civ and
            target == self.effective_target
        )

    def set_state(self, state):
        # Exit prev state
        if self.state:
            if 'exit' in self.states[self.state]:
                self.states[self.state]['exit']()

        # Enter new state
        if 'enter' in self.states[state]:
            self.states[state]['enter']()

        # Change state
        self.state = state

    def update(self, dt):
        self.time += dt
        if self.health <= 0:
            e = explosion.Explosion(self.pos, [PICO_WHITE, PICO_LIGHTGRAY, PICO_DARKGRAY], 0.25, 13, scale_fn="log", line_width=1)
            self.scene.game_group.add(e)
            self.kill()
            return

        self.states[self.state]['update'](dt)

        # Factor in fleet forces
        self.fleet_forces = self.get_fleet_forces(dt) * FLEET_POWER
        if self.fleet_forces.sqr_magnitude() > self.fleet_minimum_forces ** 2:
            self.target_velocity += self.fleet_forces

        # Try to get to the target velocity
        velocity_adjust_total = self.target_velocity - self.velocity
        velocity_adjust_frame = velocity_adjust_total.normalized() * dt * self.get_thrust_accel()
        if velocity_adjust_frame.sqr_magnitude() > velocity_adjust_total.sqr_magnitude():
            self.velocity = self.target_velocity
        else:
            self.velocity += velocity_adjust_frame

        if self.velocity.sqr_magnitude() > self.get_max_speed() ** 2:
            self.velocity = self.velocity.normalized() * self.get_max_speed()

        # Set angle based on velocity
        if self.target_heading is None:
            if self.velocity.sqr_magnitude() > 0:
                _, self.angle = self.velocity.to_polar()

        else:
            angle_delta = helper.get_angle_delta(self.angle, self.target_heading)
            if abs(angle_delta) < ROTATE_SPEED * dt:
                self.angle = self.target_heading
            elif angle_delta < 0:
                self.angle -= ROTATE_SPEED * dt
            else:
                self.angle += ROTATE_SPEED * dt

        if self.velocity.sqr_magnitude() > 0:
            if self._timers['thrust_particle_time'] > THRUST_PARTICLE_RATE:
                self.emit_thrust_particles()
                self._timers['thrust_particle_time'] = 0   

        # Nearest hazard
        nearest,dsq = helper.get_nearest(self.pos, [o for o in self.scene.get_objects() if o.collidable and o.stationary])
        if nearest and nearest != self.effective_target:
            dsf = dsq - nearest.radius ** 2
            delta = (nearest.pos - self.pos).normalized()
            self.velocity += -delta * (50 / math.sqrt(max(dsf,1))) * dt

        self.pos += self.velocity * dt
        self.health_bar.pos = self.pos + V2(0, -6)
        self.shield_bar.pos = self.pos + V2(0, -9)

        self.special_stat_update(dt)

        if self.scene.game.run_info.o2 <= 0 and self.owning_civ == self.scene.my_civ:
            self.health -= self.get_max_health() / 60 * dt

        super().update(dt)

    def emit_thrust_particles(self):
        pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
        pvel += -self.velocity / 2
        p = particle.Particle("assets/thrustparticle.png", 1, self.pos + -self.velocity.normalized() * self.radius, 1, pvel)
        self.scene.game_group.add(p)
             

    def special_stat_update(self, dt):
        # Regenerate
        self.health += self.get_stat("ship_regenerate") * dt

        self.bonus_attack_speed_time -= dt

    def collide(self, other):
        if self.can_land(other) and self.wants_to_land():
            self.kill()
            other.add_ship(self.SHIP_NAME)
            other.needs_panel_update = True
        else:
            if isinstance(other, bullet.Bullet):
                return
            if isinstance(other, ReflectorShieldObj) or isinstance(other, planet.building.ReflectorShieldCircleObj):
                return
            delta=(other.pos-self.pos).normalized()
            self.pos += -delta

    def get_fleet_forces(self, dt):
        # OPT - only calc fleet forces every so often
        if self._timers['opt_time'] > 0.2:
            self._timers['opt_time'] -= 0.2
        else:
            return self.opt_fleet_forces

        forces = V2(0,0)

        # Get the fleet
        if self.fleet is None:
            return forces
        our_ships = self.fleet.ships #self.scene.get_civ_ships(self.owning_civ)
        fleet_ships = [s for s in our_ships if (s.pos - self.pos).sqr_magnitude() <= FLEET_RADIUS ** 2]
        fleet_ships.remove(self)

        # Separation
        for ship in fleet_ships:
            delta = ship.pos - self.pos
            sm = max(delta.sqr_magnitude(),1)
            if sm < FLEET_SEPARATION_MAX ** 2:
                forces -= (delta.normalized() * (FLEET_SEPARATION_DEGRADE / sm)) * FLEET_SEPARATION_POWER

        # Proximity
        if fleet_ships:
            center = V2(0,0)
            for ship in fleet_ships:
                center += ship.pos / len(fleet_ships)

            delta = center - self.pos
            forces += delta.max(1) * FLEET_PROXIMITY_POWER

        self.opt_fleet_forces = forces.copy()
        return forces        

    def enter_state_cruising(self):
        pass

    def state_cruising(self, dt):
        if not self.chosen_target.is_alive():
            self.set_state(STATE_RETURNING)
            return

        if self.scene.flowfield.has_field(self.effective_target):
            self.target_velocity = self.scene.flowfield.get_vector(self.pos, self.effective_target, 10) * self.get_cruise_speed()
        else:
            delta = self.effective_target.pos - self.pos
            self.target_velocity = delta.normalized() * self.get_cruise_speed()            

        # Warp
        if self.get_stat("warp_drive"):
            if self._timers['warp_drive'] > 0:
                _,distsq = helper.get_nearest(self.pos, self.scene.get_planets())
                if distsq > 30 ** 2:
                    self.warp(self.get_stat("warp_drive") * 10 + 20)
                    self._timers['warp_drive'] = -20

    def warp(self, warp_dist):
        end = self.effective_target.pos
        offset_dist = self.effective_target.radius + 20
        delta = (end - self.pos)
        if warp_dist ** 2 >= delta.sqr_magnitude() or not self.scene.flowfield.has_field(self.effective_target):
            maxdist = delta.magnitude() - offset_dist
            delta = delta.normalized()
            target_pos = self.pos + delta * min(warp_dist, maxdist)
        else:
            target_pos = self.scene.flowfield.walk_field(self.pos, self.effective_target, warp_dist)

        for color in [PICO_BLUE, PICO_WHITE, PICO_DARKBLUE]:
            p = LaserParticle(self.pos + V2.random_angle() * 3, target_pos + V2.random_angle() * 3, color, random.random() / 2)
            self.scene.game_group.add(p)
        self.pos = target_pos
        self.on_warp()

    def on_warp(self):
        pass

    def enter_state_returning(self):
        nearest, dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
        if nearest:        
            self.effective_target = nearest

    def state_returning(self, dt):
        self.target_velocity = self.scene.flowfield.get_vector(self.pos, self.effective_target, 10) * self.get_cruise_speed()

    def state_waiting(self, dt):
        self.waiting_time += dt 
        _,a = (self.pos - self.effective_target.pos).to_polar()
        a += 0.2
        target_pt = self.effective_target.pos + V2.from_angle(a) * (ATMO_DISTANCE + self.effective_target.radius)
        self.target_velocity = (target_pt - self.pos).normalized() * self.get_max_speed() * 0.5

        if isinstance(self.effective_target, planet.planet.Planet):
            if self.can_land(self.effective_target):
                self.set_state(STATE_CRUISING)

    def exit_state_waiting(self):
        self.waiting_time = 0

    def kill(self):
        if self.health <= 0:
            sound.play("explosion1")
            base_angle = random.random() * 6.2818
            for x in range(self.image.get_width()):
                for y in range(self.image.get_height()):
                    color = tuple(self.image.get_at((x,y)))
                    if color[3] >= 128 and color[0:3] != PICO_BLACK:
                        _,a = (V2(x,y) - V2(5.5,5.5)).to_polar()
                        if abs(helper.get_angle_delta(a, base_angle)) > 3.14159/2:
                            a = base_angle + 3.14159
                        else:
                            a = base_angle
                        pvel = V2.from_angle(a) * 6
                        p = particle.Particle([PICO_WHITE, PICO_LIGHTGRAY, PICO_DARKGRAY],1,self.pos + V2(x - 6,y - 6),1.5,pvel)
                        self.scene.game_group.add(p)        

        if self.get_stat("ship_death_heal") > 0:
            nearby = helper.all_nearby(self.pos,[s for s in self.scene.get_civ_ships(self.owning_civ) if s is not self], FLEET_RADIUS)
            if nearby:
                other = random.choice(nearby)
                other.health += self.get_stat("ship_death_heal") # TODO: Particles!

        return super().kill()

    # STUNNED

    def state_stunned(self, dt):
        self.target_velocity = V2(0,0)
        self.target_heading = self.angle + dt * 2
        if self._timers['stun_time'] > 5:
            self.set_state(self.post_stun_state)

        if ((self._timers['stun_time'] + dt) * 20) % 1 < (self._timers['stun_time'] * 20) % 1:
            ra = V2.random_angle()
            p = particle.Particle([PICO_YELLOW, PICO_BLUE, PICO_YELLOW, PICO_BLUE], 1, self.pos + ra * 4, 0.35, ra * 10)
            self.scene.game_group.add(p)

    def enter_state_stunned(self):
        self.post_stun_state = self.state
        self._timers['stun_time'] = 0

    def exit_state_stunned(self):
        self.target_heading = None

    def command_warp(self):
        self.warp(9999)
        self.bonus_attack_speed_time = 6

    def change_owner(self, owner, target):
        self.owning_civ = owner
        self.chosen_target = target
        self.effective_target = target
        self.set_state(STATE_CRUISING)

        new_color = PICO_GREEN if owner == self.scene.my_civ else PICO_RED

        for x in range(self._sheet.get_width()):
            for y in range(self._sheet.get_height()):
                color = tuple(self._sheet.get_at((x,y)))
                if color[3] >= 128 and color[0:3] != PICO_BLACK:
                    self._sheet.set_at((x,y), new_color)
        self._update_image()