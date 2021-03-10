from colors import DARKEN_COLOR, PICO_BLACK, PICO_DARKGRAY, PICO_LIGHTGRAY, PICO_PINK, PICO_WHITE
from v2 import V2
from spaceobject import SpaceObject
from planet import planet
import random
import math
import particle
import bullet
import helper

ROTATE_SPEED = 6.2818
FLEET_RADIUS = 25
FLEET_POWER = 1.5
FLEET_SEPARATION_POWER = 2
FLEET_SEPARATION_DEGRADE = 50
FLEET_SEPARATION_MAX = 12
FLEET_PROXIMITY_POWER = 0.5
ATMO_DISTANCE = 15
WARP_PLANET_MIN_DIST = 15

THRUST_PARTICLE_RATE = 0.25

PATH_FOLLOW_CLOSENESS = 20

STATE_CRUISING = 'cruising'
STATE_RETURNING = 'returning'
STATE_WAITING = 'waiting'

class Ship(SpaceObject):
    HEALTHBAR_SIZE = (14,2)
    THRUST_ACCEL = 5
    MAX_SPEED = 8
    BASE_HEALTH = 10
    WARP_DRIVE_TIME = 30.0
    SHIP_NAME = None

    def __init__(self, scene, pos, owning_civ):
        SpaceObject.__init__(self, scene, pos)
        self.owning_civ = owning_civ
        self.offset = (0.5, 0.5)
        self.collidable = True

        # States
        self.states = {
            STATE_CRUISING:{'update':self.state_cruising},
            STATE_WAITING:{'update':self.state_waiting},
            STATE_RETURNING:{'update':self.state_returning},
        }
        self.state = None
        self.set_state(STATE_CRUISING)

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
        self._timers["movement_variation"] = random.random() * 6.2818
        self._timers['thrust_particle_time'] = 0

        self.set_health(self.get_max_health())

    def get_thrust_accel(self): return self.THRUST_ACCEL
    def get_max_speed(self): return self.MAX_SPEED
    def get_cruise_speed(self): return self.MAX_SPEED * 0.80
    def get_max_health(self): return self.BASE_HEALTH

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

        self.pos += self.velocity * dt
        self.health_bar.pos = self.pos + V2(0, -6)
        super().update(dt)

    def collide(self, other):
        if self.can_land(other) and self.wants_to_land():
            self.kill()
            other.add_ship(self.SHIP_NAME)
            other.needs_panel_update = True

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

    def state_cruising(self, dt):
        if self.path:
            delta = (self.path[0] - self.pos)
            if delta.sqr_magnitude() < PATH_FOLLOW_CLOSENESS ** 2:
                self.path.pop(0)

        if self.path:
            delta = (self.path[0] - self.pos)
            self.target_velocity = delta.normalized() * self.get_cruise_speed() * 0.8

        else:
            delta = self.effective_target.pos - self.pos
            self.target_velocity = delta.normalized() * self.get_cruise_speed() * 0.8

        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, planet.Planet):
            if (delta.magnitude() - self.effective_target.radius - ATMO_DISTANCE) <= 0:
                if not self.can_land(self.effective_target):
                    self.set_state(STATE_WAITING)    

    def state_returning(self, dt):
        pass


    def state_waiting(self, dt):
        _,a = (self.pos - self.effective_target.pos).to_polar()
        a += 0.2
        target_pt = self.effective_target.pos + V2.from_angle(a) * (ATMO_DISTANCE + self.effective_target.radius)
        self.target_velocity = (target_pt - self.pos).normalized() * self.get_max_speed() * 0.5

        if isinstance(self.effective_target, planet.Planet):
            if self.can_land(self.effective_target):
                self.set_state(STATE_CRUISING)

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
                        p = particle.Particle([color, DARKEN_COLOR.get(color[0:3],PICO_BLACK), PICO_DARKGRAY],1,self.pos + V2(x - 6,y - 6),1.25,pvel)
                        self.scene.game_group.add(p)                    

        return super().kill()