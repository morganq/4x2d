import math

import pygame

import game
import sectortitleingame
import sound
import text
from colors import *
from helper import clamp
from spritebase import SpriteBase

V2 = pygame.math.Vector2

START_TIME = 2.0
FINISH_TIME = 0.25
KILL_TIME = 8

class StageName(SpriteBase):
    def __init__(self, pos, number, name, description):
        super().__init__(pos)
        self.number = number
        self.name = name
        self.description = description
        self.time = 0
        self.layer = 20
        self.visible = False
        self.close_time = KILL_TIME - FINISH_TIME
        self.visible_time = START_TIME + 0.25
        self.played_close_sound = False
        self._generate_image()

    def _generate_image(self):
        yo = 5
        w = game.Game.inst.game_resolution.x
        t = clamp((self.time - START_TIME) / FINISH_TIME, 0, 1) ** 1.5
        t3 = text.render_multiline(self.description, "small", PICO_LIGHTGRAY, wrap_width=400, center=False)
        h = clamp(t * 8, 0, 1) * (55 + t3.get_height())
        self.image = pygame.Surface((w, h + yo * 2), pygame.SRCALPHA)        
        dx1 = t * w * 0.6
        dx2 = t * w * 0.6 + h
        z = clamp((self.time - KILL_TIME + 0.3) * 4, 0, 1) * ((h / 2) - yo)
        points = [
            (int(w / 2 - dx1), 0 + z + yo),
            (int(w / 2 + dx1), 0 + z + yo),
            (int(w / 2 + dx2), h - z - yo),
            (int(w / 2 - dx2), h - z - yo),
        ]
        for x in range(int(w/2 - dx1 - 8 + (self.time * 23) % 8), int(w/2 + dx1), 8):
            l = 4
            pygame.draw.line(self.image, PICO_WHITE, (x, yo + z - 2), (x + l, yo + z - 2), 1)
            pygame.draw.line(self.image, PICO_WHITE, (w - x, h - z - yo + 2), (w - x + l, h - z - yo + 2), 1)
        pygame.draw.polygon(self.image, PICO_DARKBLUE, points, 0)
        pygame.draw.polygon(self.image, PICO_WHITE, points, 1)
        #pygame.draw.polygon(self.image, PICO_BLACK, points, 1)
        pygame.draw.line(self.image, PICO_WHITE, points[3], points[0], 2)
        pygame.draw.line(self.image, PICO_WHITE, points[2], points[1], 2)

        if t >= 0.25 and self.time < KILL_TIME - 0.35:
            t1 = text.render_multiline("- SECTOR %d -" % self.number, "small", PICO_BLUE, wrap_width=500, center=False)
            self.image.blit(t1, (w / 2 - t1.get_width() / 2, 11))
            t2 = text.render_multiline(self.name, "big", PICO_YELLOW, wrap_width=500, center=False)
            self.image.blit(t2, (w / 2 - t2.get_width() / 2, 29))
            i = int(clamp((self.time - START_TIME - FINISH_TIME) * 0.8, 0,1) * len(self.description))
            t4 = text.render_multiline(self.description[0:i], "small", PICO_WHITE, wrap_width=400, center=False)
            self.image.blit(t4, (w / 2 - t3.get_width() / 2, 49))

        self._width = w
        self._height = h
        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        if self.time > START_TIME:
            if not self.visible:
                sound.play("msg1")
            self.visible = True
        if self.time > self.close_time and not self.played_close_sound:
            sound.play("msg2")
            self.played_close_sound = True
        if self.time > KILL_TIME:
            
            try:
                reward = game.Game.inst.run_info.get_current_level_galaxy()['rewards'][0]
            except:
                reward = None
            st = sectortitleingame.SectorTitleInGame(self.get_center(), "Sector %d: [%s]" % (self.number, self.name), reward)
            st.offset = (0.5, 0.5)
            self.groups()[0].add(st)
            self.kill()
        self._generate_image()
        return super().update(dt)
