import random

import helper
import pygame
from colors import *
from particle import Particle
from ships.all_ships import SHIPS_BY_NAME
from ships.battleship import Battleship
from spaceobject import SpaceObject
from v2 import V2

REVIVING_PLANET_CLOSE_RANGE = 50
ACCEL = 4
BRAKE = 6


class BossMothership(SpaceObject):
    STATE_CINEMATIC_TRAVELING = "cinematic_traveling"
    STATE_CINEMATIC_POPULATING = "cinematic_populating"
    STATE_GAME_WAITING = "waiting"
    STATE_GAME_TRAVELING = "traveling"
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
        self.max_speed = 6
        self.owning_civ = self.scene.enemy.civ

        self.emit = []
        self.emit_timer = 0

    def brake(self, dt):
        if self.velocity.sqr_magnitude() > 0:
            brake = -self.velocity.normalized() * BRAKE * dt
            if self.velocity.sqr_magnitude() > brake.sqr_magnitude():
                self.velocity += brake
            else:
                self.velocity = V2(0,0)

    def update(self, dt):
        self.time += dt
        self.frame = int(self.time * 3) % 15
        if self.state == self.STATE_CINEMATIC_TRAVELING:
            self.target_planet, sqdist = helper.get_nearest(self.pos, self.planets_to_revive)
            if self.target_planet:
                #delta = self.target_planet.pos - self.pos
                if sqdist < REVIVING_PLANET_CLOSE_RANGE ** 2:
                    self.state = self.STATE_CINEMATIC_POPULATING
                    self.emit = ['bosscolonist', 'bossfighter', 'bossfighter', 'bosslaser']
                    self.emit_timer = 5.0
                    evac_target = random.choice(self.scene.get_civ_planets(self.scene.my_civ))
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
            else:
                if self.emit_timer < 0:
                    if self.target_planet.owning_civ == self.scene.my_civ:
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
            self.brake(dt)

        if self.velocity.sqr_magnitude() > self.max_speed ** 2:
            self.velocity = self.velocity.normalized() * self.max_speed

        self.pos += self.velocity * dt

            
        return super().update(dt)

    def _generate_image(self):
        frames = 30
        self._width = self._height = 33
        self._frame_width = self._width
        self._sheet = pygame.Surface((self._width * frames, self._height), pygame.SRCALPHA)

        center = V2(self._width // 2, self._height // 2)
        def convert(pts, angle):
            out = []
            for pt in pts:
                d,a = pt.to_polar()
                out.append((V2.from_angle(a + angle) * d + center).tuple_int())
            return out

        a1 = 0
        a2 = 6.2818 / 3
        a3 = 6.2818 * 2 / 3

        for i in range(frames // 2):
            surf = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
            theta = i * a3 / frames
            wing = [V2(0, -1), V2(8, -2), V2(8, 2), V2(0, 1)]
            tip = [V2(8, -3), V2(9, -3), V2(9, 3), V2(8, 3)]
            pygame.draw.circle(surf, PICO_BLACK, center.tuple_int(), 6, 0)
            
            for z,a in enumerate([a1,a2,a3]):
                pygame.draw.polygon(surf, PICO_BLACK, convert(wing, a + theta), 2)
                pygame.draw.polygon(surf, PICO_BLACK, convert(tip, a + theta), 2)

            pygame.draw.circle(surf, PICO_RED, center.tuple_int(), 5, 0)
            for z,a in enumerate([a1,a2,a3]):
                pygame.draw.polygon(surf, PICO_RED, convert(wing, a + theta), 0)
                pygame.draw.polygon(surf, PICO_RED, convert(tip, a + theta), 0)
                if (i+z*2) % 6 == 0:
                    pygame.draw.circle(surf, PICO_WHITE, convert([V2(7, 0)], a + theta)[0], 1, 0)

            pygame.draw.circle(surf, PICO_BLACK, (center + V2(0,-2)).tuple_int(), 1, 0)
            pygame.draw.circle(surf, PICO_BLACK, (center + V2(2,1)).tuple_int(), 1, 0)
            pygame.draw.circle(surf, PICO_BLACK, (center + V2(-2,1)).tuple_int(), 1, 0)

            self._sheet.blit(surf, (i * self._width, 0))

        self._recalc_rect()
        self._update_image()

