from colors import *
from v2 import V2
from spaceobject import SpaceObject
from planet import planet
import random
import math
import particle
import bullet
import helper
import explosion

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

        # States
        self.states = {
            STATE_CRUISING:{'update':self.state_cruising, 'enter':self.enter_state_cruising},
            STATE_WAITING:{'update':self.state_waiting, 'exit':self.exit_state_waiting},
            STATE_RETURNING:{'update':self.state_returning, 'enter':self.enter_state_returning},
            STATE_STUNNED:{'update':self.state_stunned, 'enter':self.enter_state_stunned, 'exit':self.exit_state_stunned}
        }
        self.state = None

        # Movement vars
        self.path = None
        self.chosen_target = None
        self.effective_target = None
        self.velocity = V2(0,0)
        self.target_velocity = V2(0,0)
        self.target_heading = None # An angle, or None.
        self.fleet_forces = V2(0,0)
        self.fleet_minimum_forces = 0 # The magnitude of the fleet forces before we start caring

        # Other stuff
        self.waiting_time = 0
        self._timers["movement_variation"] = random.random() * 6.2818
        self._timers['thrust_particle_time'] = 0
        self._timers['staged_booster'] = -self.get_stat("staged_booster_time")
        self._timers['stun_time'] = 0
        self._timers['warp_drive'] = 0

        # Upgrades
        self.bonus_max_health_aura = 0
        self.slow_aura = 0

        # Stuff that has to come at the end
        self.set_health(self.get_max_health())
        self.set_state(STATE_CRUISING)

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
        if self.get_stat('ship_speed_mul_targeting_planets') and self.is_target_enemy() and isinstance(self.effective_target, planet.Planet):
            speed *= (1 + self.get_stat('ship_speed_mul_targeting_planets'))
            if random.random() < 0.02:
                p = particle.Particle([PICO_WHITE, PICO_BLUE, PICO_BLUE, PICO_DARKBLUE, PICO_DARKBLUE], 1, self.pos, 1.5, self.velocity * -1 + V2.random_angle() * 1.25)
                self.scene.game_group.add(p)    

        speed *= (1 + self.get_stat("ship_speed_mul"))
        speed *= (1 - self.slow_aura)
        return speed

    def get_cruise_speed(self): return self.get_max_speed() * 0.80

    def get_max_health(self):
        return self.BASE_HEALTH * (self.get_stat("ship_health_mul") + 1) + self.get_stat("ship_health_add") + self.bonus_max_health_aura

    def get_max_shield(self):
        shield = 0
        if self.get_stat("enclosure_shield") and self.fleet and len(self.fleet.ships) >= 8:
            shield += self.get_stat("enclosure_shield")
        if self.get_stat('ship_shield_far_from_home'):
            _, near_dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
            if near_dist > FAR_FROM_HOME_DIST ** 2:
                shield += self.get_stat('ship_shield_far_from_home')
        return shield

    def fix_path(self):
        if not self.path:
            return
        closest_path_dist = 9999999
        closest_i = 0
        for i,pt in enumerate(self.path):
            d = (pt - self.pos).sqr_magnitude()
            if d < closest_path_dist:
                closest_path_dist = d
                closest_i = i
        self.path = self.path[closest_i + 1:]        


    def wants_to_land(self):
        return True

    def set_target(self, target):
        self.chosen_target = target
        self.effective_target = target

    def set_path(self, path):
        self.path = path

    def can_land(self, target):
        return (
            isinstance(target, planet.Planet) and
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
                pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
                pvel += -self.velocity / 2
                p = particle.Particle("assets/thrustparticle.png",1,self.pos + -self.velocity.normalized() * self.radius,1,pvel)
                self.scene.game_group.add(p)
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

        super().update(dt)

    def special_stat_update(self, dt):
        # Regenerate
        self.health += self.get_stat("ship_regenerate") * dt

        # Strafe
        # TODO: implement

    def collide(self, other):
        if self.can_land(other) and self.wants_to_land():
            self.kill()
            other.add_ship(self.SHIP_NAME)
            other.needs_panel_update = True
        else:
            if isinstance(other, bullet.Bullet):
                return
            delta=(other.pos-self.pos).normalized()
            self.pos += -delta

    def get_fleet_forces(self, dt):
        forces = V2(0,0)

        # Get the fleet
        our_ships = self.scene.get_civ_ships(self.owning_civ)
        fleet_ships = [s for s in our_ships if (s.pos - self.pos).sqr_magnitude() <= FLEET_RADIUS ** 2]
        fleet_ships.remove(self)

        # Separation
        for ship in fleet_ships:
            delta = ship.pos - self.pos
            sm = delta.sqr_magnitude()
            if sm < FLEET_SEPARATION_MAX ** 2:
                forces -= (delta.normalized() * (FLEET_SEPARATION_DEGRADE / sm)) * FLEET_SEPARATION_POWER

        # Proximity
        if fleet_ships:
            center = V2(0,0)
            for ship in fleet_ships:
                center += ship.pos / len(fleet_ships)

            delta = center - self.pos
            forces += delta.max(1) * FLEET_PROXIMITY_POWER

        return forces        

    def enter_state_cruising(self):
        self.fix_path()

    def state_cruising(self, dt):
        if not self.chosen_target.is_alive():
            self.set_state(STATE_RETURNING)
            return
            
        if self.path:
            delta = (self.path[0] - self.pos)
            if delta.sqr_magnitude() < PATH_FOLLOW_CLOSENESS ** 2:
                self.path.pop(0)

        if self.path:
            delta = (self.path[0] - self.pos)
            self.target_velocity = delta.normalized() * self.get_cruise_speed()

        else:
            delta = self.effective_target.pos - self.pos
            self.target_velocity = delta.normalized() * self.get_cruise_speed()

        # Warp
        if self.get_stat("warp_drive") and self.path:
            if self._timers['warp_drive'] > 0:
                _,distsq = helper.get_nearest(self.pos, self.scene.get_planets())
                if distsq > 30 ** 2:
                    end = self.effective_target.pos
                    offset_dist = self.effective_target.radius + 10
                    if len(self.path) > 5:
                        end = self.path[5]
                        offset_dist = 0
                    delta = (end - self.pos)
                    md = delta.magnitude() - offset_dist
                    delta = delta.normalized()
                    self.pos += delta * min((self.get_stat("warp_drive") * 10 + 20), md)

                    self.fix_path()
                    self._timers['warp_drive'] = -20
                    self.on_warp()

    def on_warp(self):
        pass

    def enter_state_returning(self):
        if self.path:
            return
        nearest, dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
        if nearest:        
            self.path = self.scene.pathfinder.find_path(self, nearest)
            self.effective_target = nearest

    def state_returning(self, dt):
        if self.path:
            delta = (self.path[0] - self.pos)
            if delta.sqr_magnitude() < PATH_FOLLOW_CLOSENESS ** 2:
                self.path.pop(0)

        if self.path:
            delta = (self.path[0] - self.pos)
            self.target_velocity = delta.normalized() * self.get_cruise_speed()

        else:
            delta = self.effective_target.pos - self.pos
            self.target_velocity = delta.normalized() * self.get_cruise_speed()
        

    def state_waiting(self, dt):
        self.waiting_time += dt 
        _,a = (self.pos - self.effective_target.pos).to_polar()
        a += 0.2
        target_pt = self.effective_target.pos + V2.from_angle(a) * (ATMO_DISTANCE + self.effective_target.radius)
        self.target_velocity = (target_pt - self.pos).normalized() * self.get_max_speed() * 0.5

        if isinstance(self.effective_target, planet.Planet):
            if self.can_land(self.effective_target):
                self.set_state(STATE_CRUISING)

    def exit_state_waiting(self):
        self.waiting_time = 0

    def kill(self):
        if self.health <= 0:
            base_angle = random.random() * 6.2818
            for x in range(self._width):
                for y in range(self._height):
                    color = tuple(self.image.get_at((x,y)))
                    if color[3] >= 128:
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