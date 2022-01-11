import math
import random

import helper
import particle
import pygame
import sound
import text
from colors import *
from explosion import Explosion
from planet.planet import Planet
from pygame.transform import threshold
from resources import resource_path
from ships.all_ships import SHIPS_BY_NAME
from simplesprite import SimpleSprite
import pygame
V2 = pygame.math.Vector2

FREEZE_INTERVAL = 90

class TimeCrystal(Planet):
    def __init__(self, scene, pos, size, resources):
        super().__init__(scene, pos, size, resources)
        self.freeze_timer = 30 #FREEZE_INTERVAL
        self.frozen_ships = []
        self.frozen_replicas = []
        self.exp = None
        self.countdown = text.Text("", "tiny", self.pos + V2(0,-4), PICO_YELLOW, border=PICO_BLACK)
        self.countdown.offset = (0.5, 0.5)
        self.scene.ui_group.add(self.countdown)


    def generate_stranded_ships(self):
        stranded_ships = ['fighter', 'colonist', 'fighter', 'colonist']
        if random.random() > 0.5:
            stranded_ships.append('bomber')
        else:
            stranded_ships.append('interceptor')
        theta = random.random() * 6.2818
        for ship in stranded_ships:
            p = self.pos + helper.from_angle(theta) * random.randint(18,32)
            s = SHIPS_BY_NAME[ship](self.scene, p, self.scene.player_civ)
            if ship == 'colonist':
                s.set_pop(random.randint(2,5))
            self.scene.game_group.add(s)
            self.freeze(s)
            theta += random.random() + 0.1

    def generate_base_art(self):
        w = h = self.radius * 2
        self.art = pygame.image.load(resource_path("assets/timecrystal.png"))

    def _generate_base_frames(self):
        self._sheet = self.art
        self._frame_width = 29
        self._width = self._frame_width
        self._height = 37
        self.art_inactive = self._sheet.subsurface((0,0,self._frame_width, self._height))
        self.art_hover = self._sheet.subsurface((self._frame_width,0,self._frame_width, self._height))
        self._recalc_rect()

    def _generate_frames(self):
        return

    def special_update(self, dt):
        self.freeze_timer -= dt
        if self.freeze_timer < 0:
            radius = 60
            self.freeze_timer += FREEZE_INTERVAL
            self.exp = Explosion(self.pos, [PICO_BLUE, PICO_PINK,PICO_BLUE, PICO_PINK,PICO_BLUE, PICO_PINK], 1.0, radius, line_width=3)
            self.scene.game_group.add(self.exp)

        self.countdown.set_text("%d" % math.ceil(self.freeze_timer))

        if self.exp:
            for s in self.scene.get_civ_ships(self.scene.player_civ):
                if (s.pos - self.exp.pos).length_squared() < self.exp.size ** 2:
                    self.freeze(s)
            if not self.exp.alive():
                self.exp = None

        return super().special_update(dt)

    def freeze(self, s):
        self.frozen_ships.append(s)
        self.scene.game_group.remove(s)
        replica = self.make_frozen_sprite(s)
        self.frozen_replicas.append(replica)
        self.scene.game_group.add(replica)

    def make_frozen_sprite(self, ship):
        outline_mask = pygame.mask.from_surface(ship.image, 127)
        surf = outline_mask.to_surface(setcolor=(*PICO_WHITE,255), unsetcolor=(0,0,0,0))      

        color_mask = pygame.mask.from_threshold(ship.image, (*PICO_GREEN,255), (2,2,2,255))
        surf2 = color_mask.to_surface(setcolor=(*PICO_BLUE,255), unsetcolor=(0,0,0,0))
        surf.blit(surf2,(0,0))
        s = SimpleSprite(ship.pos, surf)
        s.offset = (0.5,0.5)
        return s

    def on_die(self):
        super().on_die()
        self.kill()

    def kill(self):
        for ship in self.frozen_ships:
            self.unfreeze_ship(ship)
        for replica in self.frozen_replicas:
            replica.kill()
        self.countdown.kill()

        sound.play_explosion()
        base_angle = random.random() * 6.2818
        for x in range(self.image.get_width()):
            for y in range(self.image.get_height()):
                color = tuple(self.image.get_at((x,y)))
                if color[3] >= 128 and color[0:3] != PICO_BLACK:
                    _,a = (V2(x,y) - V2(self.width/2,self.height/2)).to_polar()
                    ad = abs(helper.get_angle_delta(a, base_angle))
                    if ad > 3.14159/2:
                        a = base_angle + 3.14159
                    else:
                        a = base_angle
                    pvel = helper.from_angle(a) * 6
                    p = particle.Particle([
                        color[0:3],
                        color[0:3],
                        DARKEN_COLOR[color[0:3]]
                        ],
                        1,
                        self.pos + V2(x - self.width // 2,y - self.height // 2),
                        1.25 + random.random() ** 2,
                        pvel
                    )
                    self.scene.game_group.add(p)  

        return super().kill()

    def unfreeze_ship(self, ship):
        self.scene.game_group.add(ship)
        ship.set_state("returning")

    def is_buildable(self):
        return False
