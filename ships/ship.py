import math
import random

import bullet
import explosion
import game
import helper
import particle
import planet
import pygame
import sound
from colors import *
from elements import shake
from framesprite import FrameSprite
from laserparticle import LaserParticle
from resources import resource_path
from satellite import ReflectorShieldObj
from spaceobject import SpaceObject
from upgrade.spacemine import SpaceMine
from v2 import V2

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

NO_PATH_RANGE = 40

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
    DISPLAY_NAME = None

    DOGFIGHTS = False
    BOMBS = False

    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        SpaceObject.__init__(self, scene, pos)
        self._base_sheet = None
        self.owning_civ = owning_civ
        self.offset = (0.5, 0.5)
        self.collidable = True
        self.collision_radius = 3
        self.stationary = False
        self.fleet = None
        self.origin = None # Planet we were emitted from

        self.fuel_remaining = self.get_max_fuel()

        self.defending = None
        self.stealth = False

        self._layer = 1

        # States
        self.states = {
            STATE_CRUISING:{'update':self.state_cruising, 'enter':self.enter_state_cruising},
            STATE_WAITING:{'update':self.state_waiting, 'exit':self.exit_state_waiting},
            STATE_RETURNING:{'update':self.state_returning, 'enter':self.enter_state_returning},
            STATE_STUNNED:{'update':self.state_stunned, 'enter':self.enter_state_stunned, 'exit':self.exit_state_stunned},
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

        self._timers['bonus_speed_particle_time'] = 0


        # Upgrades
        self.bonus_max_health_aura = 0
        self.bonus_attack_speed_time = 0
        self.slow_aura = 0
        self.extra_shield = 0

        # Alien stuff
        self.tether_target = False

        # Cinematic stuff
        self.cinematic_no_combat = False

        # Turnaround
        self.turnaround_spr = None
        self.turnaround_time = 0

        # Stuff that has to come at the end
        self.set_health(self.get_max_health())
        self.set_state(STATE_CRUISING)

        self.debug_ratio = 0

        # opt
        self._timers['opt_time'] = random.random()
        self.opt_fleet_forces = V2(0,0)

        self.updated_color = False
        self.visible = False

    def get_max_fuel(self):
        return self.owning_civ.get_ship_fuel(self.SHIP_BONUS_NAME)

    def _set_player_ship_sprite_sheet(self, size=12):
        lvl = self.scene.game.run_info.ship_levels[self.SHIP_BONUS_NAME]
        if lvl == 1:
            self.set_sprite_sheet("assets/%s.png" % self.SHIP_BONUS_NAME, size)
        else:
            self.set_sprite_sheet("assets/%s_lvl%d.png" % (self.SHIP_BONUS_NAME, lvl), size)

    @classmethod
    def estimate_flight_range(cls, civ, target=None):
        dist = civ.get_ship_fuel(cls.SHIP_BONUS_NAME) * (1 + civ.get_stat("ship_speed_mul"))
        if target and target.owning_civ != civ:
            dist *= (1 + civ.get_stat('ship_speed_mul_targeting_planets'))
        return dist

    @classmethod
    def get_display_name(cls):
        return (cls.DISPLAY_NAME or cls.SHIP_NAME).title()

    def get_stat(self, stat):
        return super().get_stat(stat) + self.owning_civ.get_stat(stat)

    def take_damage(self, damage, origin=None):
        armor = 0
        if self.get_stat("ship_armor_far_from_home"):
            nearest, dist = helper.get_nearest(self.pos, self.scene.get_civ_planets(self.owning_civ))
            if dist > FAR_FROM_HOME_DIST ** 2:
                armor = self.get_stat("ship_armor_far_from_home")
        armor += self.get_stat("ship_armor")
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

    def is_target_not_ally(self):
        return self.effective_target and self.effective_target.owning_civ != self.owning_civ

    def is_in_deep_space(self):
        nearest, distsq = helper.get_nearest(self.pos, self.scene.get_planets())
        return distsq > DEEP_SPACE_DIST ** 2

    def get_max_speed(self):
        speed = self.MAX_SPEED
        if self.get_stat("deep_space_drive") and self.is_in_deep_space():
            speed *= (1 + self.get_stat("deep_space_drive"))
        if self._timers['staged_booster'] < 0:
            speed *= 2
        if self.get_stat('ship_speed_mul_targeting_planets') and self.is_target_not_ally() and isinstance(self.effective_target, planet.planet.Planet):
            speed *= (1 + self.get_stat('ship_speed_mul_targeting_planets'))

        speed *= (1 + self.get_stat("ship_speed_mul"))
        speed *= (1 - self.slow_aura)
        return speed

    def get_cruise_speed(self): return self.get_max_speed() * 0.80

    def get_max_health(self):
        mhp = self.BASE_HEALTH * (self.get_stat("ship_health_mul") + 1) + self.get_stat("ship_health_add") + self.bonus_max_health_aura
        return mhp

    def add_shield(self, val):
        self.extra_shield += val
        self.shield += val
        self.shield_bar.show()

    def get_max_shield(self):
        shield = self.extra_shield
        if self.get_stat("enclosure_shield") and self.fleet and len(self.fleet.ships) >= 4:
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
        self.starting_pos = self.pos

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

    def _generate_stealth_image(self):
        self.image.fill((0,0,0,0))
        op = self.top_left + V2(math.sin(self.time * 3.4) * 2, math.cos(self.time * 5.1) * 2)
        self.image.blit(self.scene.background.image, (0,0), (*op.tuple_int(), self.width, self.height))
        mask = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255,255,255), (self.width // 2, self.height // 2), self.width // 2, 0)
        self.image.blit(mask, (0,0), None, pygame.BLEND_RGBA_MULT)

    def update(self, dt):
        if not self.updated_color:
            self.update_color()
            self.updated_color = True
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

        # We want to reduce thrust if we're trying to thrust away from our heading
        angle_thrust_adjust = 1
        velocity_adjust_final = velocity_adjust_total.normalized()
        current_heading_vec = V2.from_angle(self.angle)
        dp = velocity_adjust_final.dot(current_heading_vec)
        if dp < 0: # dot product < 0 means that the two vectors are facing away from eachother.
            angle_thrust_adjust = 0.5

        velocity_adjust_frame = velocity_adjust_final * dt * self.get_thrust_accel() * angle_thrust_adjust
        if velocity_adjust_frame.sqr_magnitude() > velocity_adjust_total.sqr_magnitude() * angle_thrust_adjust:
            self.velocity = self.target_velocity * angle_thrust_adjust
        else:
            self.velocity += velocity_adjust_frame

        if self.velocity.sqr_magnitude() > (self.get_max_speed() * angle_thrust_adjust) ** 2:
            self.velocity = self.velocity.normalized() * self.get_max_speed() * angle_thrust_adjust

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
            near = 20
            if dsf > 0 and dsf < near ** 2:
                t = 1 - math.sqrt(dsf) / near
                self.velocity += -delta * t * 5 * dt
                side = V2(delta.y, -delta.x)
                fwd = self.velocity.normalized()
                cross = fwd.cross(side)
                if cross > 0:
                    side = -side
                self.velocity += side * t * 5 * dt


        # Stay away from the edges of the world
        if self.pos.x < 5:
            self.velocity.x += dt * self.get_thrust_accel() * 2
        if self.pos.y < 5:
            self.velocity.y += dt * self.get_thrust_accel() * 2
        if self.pos.x > game.Game.inst.game_resolution.x - 5:
            self.velocity.x -= dt * self.get_thrust_accel() * 2
        if self.pos.y > game.Game.inst.game_resolution.y - 5:
            self.velocity.y -= dt * self.get_thrust_accel() * 2                        

        if self.state == STATE_CRUISING:
            speed_adjust = self.get_max_speed() / self.MAX_SPEED
            cruise_travel_dist_frame = self.velocity.magnitude() * dt / speed_adjust
            self.fuel_remaining -= cruise_travel_dist_frame

            if self.fuel_remaining < 0:
                sound.play("recall")
                self.set_state(STATE_RETURNING)
                self.turnaround_spr = FrameSprite(self.pos, "assets/fighterturnaround.png", 6)
                self.scene.ui_group.add(self.turnaround_spr)
                self.turnaround_time = 0
                # TODO: Error sound
                
        self.pos += self.velocity * dt
        self.health_bar.pos = self.pos + V2(0, -6)
        self.shield_bar.pos = self.pos + V2(0, -9)

        self.special_stat_update(dt)

        if self.scene.game.run_info.o2 <= 0 and self.owning_civ and self.owning_civ.is_player:
            self.health -= self.get_max_health() / 60 * dt

        super().update(dt)

        if self.stealth:
            self._generate_stealth_image()       
            self._timers['thrust_particle_time'] = -1

    def emit_thrust_particles(self):
        pvel = V2(random.random() - 0.5, random.random() - 0.5) * 5
        pvel += -self.velocity / 2
        p = particle.Particle("assets/thrustparticle.png", 1, self.pos + -self.velocity.normalized() * self.radius, 1, pvel)
        self.scene.game_group.add(p)
             

    def special_stat_update(self, dt):
        # Regenerate
        self.health += self.get_stat("ship_regenerate") * dt

        self.bonus_attack_speed_time -= dt

        speed_factor = self.get_max_speed() / self.MAX_SPEED
        if speed_factor > 1:
            if self._timers['bonus_speed_particle_time'] > 0.15 / speed_factor:
                #e = explosion.Explosion(self.pos + V2.random_angle(), [PICO_BLUE, PICO_BLUE, PICO_BLUE, PICO_WHITE, PICO_WHITE, PICO_BLUE], 0.25, 3, line_width=1)
                colors = [PICO_WHITE, PICO_BLUE, PICO_GREEN, PICO_PINK, PICO_PURPLE]
                n = int((speed_factor - 1) * 3) + 1
                colors = colors[0:n]
                #ang = self.velocity.to_polar()[1] + 3.14159 + (random.random() - 0.5) * 3
                ang = self.velocity.to_polar()[1] + 3.14159 + (random.random() - 0.5) * 0.45 + math.sin(self.time * 3 * speed_factor)
                p = particle.Particle([random.choice(colors)], 1, self.pos + -self.velocity.normalized() * self.radius, 0.6, V2.from_angle(ang) * 8)
                self.scene.game_group.add(p)
                self._timers['bonus_speed_particle_time'] = 0

    def collide(self, other):
        if self.can_land(other) and self.wants_to_land():
            self.kill()
            other.add_ship(self.SHIP_NAME, notify=False)
            other.needs_panel_update = True
        else:
            if isinstance(other, bullet.Bullet):
                return
            if isinstance(other, ReflectorShieldObj) or isinstance(other, planet.building.ReflectorShieldCircleObj):
                return
            if not other.solid:
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

        delta = self.effective_target.pos - self.pos
        use_path = True
        if not self.scene.flowfield.has_field(self.effective_target) or delta.sqr_magnitude() < NO_PATH_RANGE ** 2:
            use_path = False

        if use_path:
            towards_flow = self.scene.flowfield.get_vector(self.pos, self.effective_target, 0)
            towards_center = towards_flow
            distance = 1
            if self.fleet and len(self.fleet.path) > 2 and len(self.fleet.ships) > 1:
                distance = (self.fleet.path[2] - self.pos).magnitude()
                towards_center = (self.fleet.path[2] - self.pos).normalized()
            ratio = 0.5
            
            ratio = helper.clamp(20 / (distance + 1), 0, 1)
            self.debug_ratio = ratio
            self.target_velocity = (towards_flow * ratio + towards_center * (1 - ratio)) * self.get_cruise_speed()

        else:
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
        delta_magnitude = delta.magnitude()
        if warp_dist >= (delta_magnitude - offset_dist) or not self.scene.flowfield.has_field(self.effective_target):
            maxdist = delta_magnitude - offset_dist
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
            self.set_target(nearest)

    def state_returning(self, dt):
        if self.fuel_remaining <= 0 and self.turnaround_spr:
            self.turnaround_time += dt
            self.turnaround_spr.pos = self.pos + V2(3, -8)
            if self.turnaround_time < 1:
                self.turnaround_spr.frame = min(int(self.turnaround_time * 4), 3)
            else:
                self.turnaround_spr.frame = int(self.turnaround_time * 4) % 2 + 2
            if self.turnaround_time > 8:
                self.turnaround_spr.kill()
                self.turnaround_spr = None
            

        if self.effective_target.owning_civ != self.owning_civ:
            self.set_state(STATE_RETURNING)
        elif self.effective_target:
            self.target_velocity = self.scene.flowfield.get_vector(self.pos, self.effective_target, 10) * self.get_cruise_speed()
        else:
            self.set_state(STATE_WAITING)

    def state_waiting(self, dt):
        self.waiting_time += dt 
        if not self.effective_target:
            return

        # If we have a target, we want to orbit it.
        delta = self.pos - self.effective_target.pos
        _,a = delta.to_polar()
        # Create a target point which is a step around the circle compared to my angle around the circle.
        a += 0.2
        target_pt = self.effective_target.pos + V2.from_angle(a) * (ATMO_DISTANCE + self.effective_target.radius)
        # Adjust our velocity to aim at this target point
        self.target_velocity = (target_pt - self.pos).normalized() * self.get_max_speed() * 0.5

        if isinstance(self.effective_target, planet.planet.Planet):
            if self.can_land(self.effective_target):
                self.set_state(STATE_CRUISING)

    def exit_state_waiting(self):
        self.waiting_time = 0

    def kill(self):
        if self.turnaround_spr:
            self.turnaround_spr.kill()
        if self.health <= 0:
            shake.shake(self.scene, self.pos, 7, 0.3)

            if self.owning_civ.ships_dropping_mines > 0:
                self.owning_civ.ships_dropping_mines -= 1
                m = SpaceMine(self.scene, self.pos, self.owning_civ, 0)
                self.scene.game_group.add(m)
                            
            sound.play_explosion()
            self.owning_civ.ships_lost += 1 # For score + stats
            self.space_explode()      

            if self.get_stat("ship_death_heal") > 0:
                nearby = helper.all_nearby(self.pos,[s for s in self.scene.get_civ_ships(self.owning_civ) if s is not self], FLEET_RADIUS)
                if nearby:
                    other = random.choice(nearby)
                    other.health += self.get_stat("ship_death_heal") # TODO: Particles!

            if self.origin:
                self.origin.emitted_ship_died(self)

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
        self.update_color()

    def update_color(self):
        color = self.owning_civ.color
        self.set_color(color)
        self.visible = True

    def set_color(self, color):
        if not self._base_sheet:
            self._base_sheet = self._sheet.copy()
        outline_mask = pygame.mask.from_surface(self._base_sheet, 127)
        surf = outline_mask.to_surface(setcolor=(*PICO_BLACK,255), unsetcolor=(0,0,0,0))      

        color_mask = pygame.mask.from_threshold(self._base_sheet, (*PICO_RED,255), (2,2,2,255))
        surf2 = color_mask.to_surface(setcolor=(*color,255), unsetcolor=(0,0,0,0))
        surf.blit(surf2,(0,0))

        white_mask = pygame.mask.from_threshold(self._base_sheet, (*PICO_WHITE,255), (2,2,2,255))
        surf3 = white_mask.to_surface(setcolor=(*PICO_WHITE,255), unsetcolor=(0,0,0,0))
        surf.blit(surf3,(0,0))

        self._sheet = surf

        self._update_image()
