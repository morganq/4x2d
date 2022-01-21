import random

import helper
import pygame
from colors import *
from healthy import Healthy
from laserparticle import LaserParticle
from particle import Particle
from planet import planet
from rangeindicator import RangeIndicator
from ships.all_ships import SHIPS_BY_NAME
from ships.battleship import Battleship
from simplesprite import SimpleSprite
from spaceobject import SpaceObject
from spritebase import SpriteBase

V2 = pygame.math.Vector2

REVIVING_PLANET_CLOSE_RANGE = 50
ACCEL = 4
BRAKE = 6
REINCARNATE_RANGE = 65

class Soul(SimpleSprite):
    def __init__(self, pos, ship):
        super().__init__(pos, "assets/soul.png")
        self.offset = (0.5,0.5)
        self.ship = ship
        self.time = 0

    def update(self, dt):
        self.time += dt
        if self.time > 5:
            self.ship.set_health(self.ship.get_max_health())
            self.ship.scene.game_group.add(self.ship)
            self.kill()
        return super().update(dt)

class BossMothership(SpaceObject):
    STATE_CINEMATIC_TRAVELING = "cinematic_traveling"
    STATE_CINEMATIC_POPULATING = "cinematic_populating"
    STATE_GAME_WAITING = "waiting"
    STATE_GAME_TRAVELING = "traveling"
    HEALTHBAR_SIZE = (50,4)
    def __init__(self, scene, pos):
        super().__init__(scene, pos)
        self.time = 0
        self._generate_image()
        self.target_planet = None
        self.velocity = V2(0,0)
        self.state = self.STATE_CINEMATIC_TRAVELING
        self.planets_to_revive = []
        self.reviving_planets = True
        self.emitted_ships = False
        self.max_speed = 4
        self.owning_civ = self.scene.enemy.civ
        self.jumped = False
        self.selectable = True
        self.collision_radius = 12
        self.collidable = True
        self.stationary = False
        self.wander_time = 0
        self.wander_center = V2(0,0)
        self.wander_point = V2(0,0)
        self.radius = 10

        self.emit = []
        self.ships_on_board = ['bossfighter','bossfighter','bossfighter','bossfighter','bossfighter','bossfighter','bosslaser','bosslaser','bosslaser']
        random.shuffle(self.ships_on_board)
        self.emit_timer = 0

        self.travel_target = None
        self.wait_time = 5

        self.set_health(self.get_max_health())
        self.range_indicator = None
        self.allied_ships_in_range = []
        self.souls = []

    def get_max_health(self):
        return 3200

    def brake(self, dt):
        if self.velocity.length_squared() > 0:
            brake = -helper.try_normalize(self.velocity) * BRAKE * dt
            if self.velocity.length_squared() > brake.length_squared():
                self.velocity += brake
            else:
                self.velocity = V2(0,0)

    def collide(self, other):
        if other.stationary:
            delta = other.pos - self.pos
            dist = delta.length()
            if dist > 0:
                overlap = (self.collision_radius + other.collision_radius) - dist
                push = helper.try_normalize(delta) * -overlap
                self.pos += push

    def wander(self, dt):
        self.wander_time -= dt
        if self.wander_time < 0:
            self.wander_time = 5
            self.wander_point = self.wander_center + helper.random_angle() * random.random() * 30
        delta = self.wander_point - self.pos
        if delta.length_squared() < 10 ** 2 or self.wander_time < 1:
            self.brake(dt)
        else:
            self.velocity += helper.try_normalize(delta) * ACCEL * dt

    def update(self, dt):
        self.time += dt

        self.health_bar.pos = self.pos + V2(0, -self.height / 2)

        if self.time > 1.0 and not self.jumped:
            self.jumped = True
            bad_location = True
            i = 0
            while bad_location:
                np = V2(self.scene.game.game_resolution.x * 0.66, self.scene.game.game_resolution.y * 0.4) + helper.random_angle() * random.random() * (50 + i * 10)
                _, dsq = helper.get_nearest(np, self.scene.get_planets())
                if dsq > 50 ** 2:
                    bad_location = False
                i += 1
            delta = np - self.pos
            dn = helper.try_normalize(delta)
            side = V2(dn.y, -dn.x)
            for i in range(12):
                color = random.choice([PICO_RED, PICO_RED, PICO_ORANGE, PICO_YELLOW, PICO_WHITE])
                z = random.randint(-12, 12)
                l1 = LaserParticle(self.pos + side * z/2, np - dn * (10 - abs(z)) + side * z, color, random.random())
                self.scene.game_group.add(l1)
            self.pos = np

        self.frame = int(self.time * 3) % 15
        if self.state == self.STATE_CINEMATIC_TRAVELING:
            self.target_planet, sqdist = helper.get_nearest(self.pos, self.planets_to_revive)
            if self.target_planet:
                #delta = self.target_planet.pos - self.pos
                if sqdist < REVIVING_PLANET_CLOSE_RANGE ** 2:
                    self.state = self.STATE_CINEMATIC_POPULATING
                    self.emit = ['bosscolonist']
                    num = 2
                    if len(self.planets_to_revive) == len(self.ships_on_board):
                        num = 1
                    if len(self.planets_to_revive) > len(self.ships_on_board):
                        num = 0   
                    for i in range(num):
                        self.emit.append(self.ships_on_board.pop(0))
                    self.emit_timer = 5.0
                    if self.target_planet.owning_civ == self.scene.player_civ:
                        possible_evacs = self.scene.get_civ_planets(self.scene.player_civ)
                        possible_evacs.remove(self.target_planet)
                        if possible_evacs:
                            possible_evacs = helper.nearest_order(V2(0, self.scene.game.game_resolution.y//2), possible_evacs)
                            evac_target = random.choice(possible_evacs[0:3])
                            for ship, amt in self.target_planet.ships.items():
                                for i in range(amt):
                                    self.target_planet.emit_ship(ship, {"to":evac_target})
                            if self.target_planet.population:
                                self.target_planet.emit_ship("colonist", {"to":evac_target, "num":self.target_planet.population})
                    return
                towards_planet = self.scene.flowfield.get_vector(self.pos, self.target_planet, 5)
                self.velocity += towards_planet * dt * ACCEL

        if self.state == self.STATE_CINEMATIC_POPULATING:
            self.brake(dt)
            self.emit_timer -= dt
            if not self.emit:
                if self.emit_timer < -3:
                    self.planets_to_revive.remove(self.target_planet)
                    if self.planets_to_revive:
                        self.state = self.STATE_CINEMATIC_TRAVELING
                    else:
                        self.state = self.STATE_GAME_WAITING
                        self.range_indicator = RangeIndicator(self.pos, REINCARNATE_RANGE, PICO_ORANGE, 1, 5)
                        self.scene.ui_group.add(self.range_indicator)
            else:
                if self.emit_timer < 0:
                    if self.target_planet.owning_civ == self.scene.player_civ:
                        self.target_planet.change_owner(None)
                    self.emit_timer = 1.0
                    name = self.emit.pop(0)
                    ctor = SHIPS_BY_NAME[name]
                    ship = ctor(self.scene, self.pos, self.owning_civ)
                    if 'colonist' in name:
                        ship.set_pop(3)
                    ship.set_target(self.target_planet)
                    self.scene.game_group.add(ship)
                    pass
        
        if self.state == self.STATE_GAME_WAITING:
            self.wander(dt)
            self.wait_time -= dt
            if self.wait_time < 0:
                self.state = self.STATE_GAME_TRAVELING
                self.travel_target = None

        if self.state == self.STATE_GAME_TRAVELING:
            if not self.travel_target:
                # Pick only fleets targeting a neutral or player planet
                fleets = [
                    f for f in self.scene.fleet_managers['enemy'].current_fleets
                    if f.target.owning_civ != self.owning_civ and isinstance(f.target, planet.Planet)
                ]
                if fleets:
                    self.travel_target = random.choice(fleets).target
                else:
                    self.state = self.STATE_GAME_WAITING
                    self.wait_time = 5
                    self.wander_center  = V2(self.pos)
            if self.travel_target:
                delta = self.travel_target.pos - self.pos
                if delta.length_squared() > (REINCARNATE_RANGE - 10) ** 2:
                    accel = self.scene.flowfield.get_vector(self.pos, self.travel_target, 10) * ACCEL
                    self.velocity += accel * dt
                else:
                    self.state = self.STATE_GAME_WAITING
                    self.wander_center  = V2(self.pos)
                    self.wait_time = 30

        objs = self.scene.get_planets() + self.scene.get_hazards()
        nearest, dsq = helper.get_nearest(self.pos, objs)
        if dsq < 40 ** 2:
            delta = nearest.pos - self.pos
            self.velocity += -helper.try_normalize(delta) * ACCEL / 2 * dt

        if self.velocity.length_squared() > self.max_speed ** 2:
            self.velocity = helper.try_normalize(self.velocity) * self.max_speed

        self.pos += self.velocity * dt
        if self.range_indicator:
            self.range_indicator.pos = self.pos

        if self.state in [self.STATE_GAME_WAITING, self.STATE_GAME_TRAVELING]:
            self.update_reincarnation()
            
        return super().update(dt)

    def update_reincarnation(self):
        nearby_ships = self.scene.get_my_ships_in_range(self.owning_civ, self.pos, REINCARNATE_RANGE)
        all_ships = set(self.allied_ships_in_range + nearby_ships)
        soul_ships = [s.ship for s in self.souls]
        for ship in all_ships:
            if ship.health <= 0 and ship not in soul_ships:
                soul = Soul(ship.pos, ship)
                self.souls.append(soul)
                self.scene.game_group.add(soul)
        self.allied_ships_in_range = nearby_ships[::]

    def _generate_image(self):
        frames = 30
        self._width = self._height = 33
        self._frame_width = self._width
        self._sheet = pygame.Surface((self._width * frames, self._height), pygame.SRCALPHA)

        center = V2(self._width // 2, self._height // 2)
        def convert(pts, angle):
            out = []
            for pt in pts:
                d,a = pt.as_polar()
                a *= 3.14159 / 180
                out.append((helper.from_angle(a + angle) * d + center))
            return out

        a1 = 0
        a2 = 6.2818 / 3
        a3 = 6.2818 * 2 / 3

        for i in range(frames // 2):
            surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
            theta = i * a3 / frames
            wing = [V2(0, -1), V2(8, -2), V2(8, 2), V2(0, 1)]
            tip = [V2(8, -3), V2(9, -3), V2(9, 3), V2(8, 3)]
            pygame.draw.circle(surf, PICO_BLACK, center, 6, 0)
            
            for z,a in enumerate([a1,a2,a3]):
                pygame.draw.polygon(surf, PICO_BLACK, convert(wing, a + theta), 2)
                pygame.draw.polygon(surf, PICO_BLACK, convert(tip, a + theta), 2)

            pygame.draw.circle(surf, PICO_RED, center, 5, 0)
            for z,a in enumerate([a1,a2,a3]):
                pygame.draw.polygon(surf, PICO_RED, convert(wing, a + theta), 0)
                pygame.draw.polygon(surf, PICO_RED, convert(tip, a + theta), 0)
                if (i+z*2) % 6 == 0:
                    pygame.draw.circle(surf, PICO_WHITE, convert([V2(7, 0)], a + theta)[0], 1, 0)

            pygame.draw.circle(surf, PICO_BLACK, (center + V2(0,-2)), 1, 0)
            pygame.draw.circle(surf, PICO_BLACK, (center + V2(2,1)), 1, 0)
            pygame.draw.circle(surf, PICO_BLACK, (center + V2(-2,1)), 1, 0)

            self._sheet.blit(surf, (i * self._width, 0))

        self._recalc_rect()
        self._update_image()


    def get_selection_info(self):
        return {'type':'boss'}

    def kill(self):
        pass
