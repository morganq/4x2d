import math
import random

import pygame

import game
import helper
import text
from colors import *
from helper import clamp, get_nearest_pos, nearest_order_pos
from resources import resource_path
from spritebase import SpriteBase

V2 = pygame.math.Vector2


class NewGameBackground(SpriteBase):
    def __init__(self, pos):
        super().__init__(pos)

        res = game.Game.inst.game_resolution
        self.background = pygame.Surface(res, pygame.SRCALPHA)
        self.background.fill(PICO_DARKGREEN)
        for i in range(400):
            color = PICO_LIGHTGRAY
            if random.random() < 0.25:
                color = PICO_WHITE
            
            if random.random() < 0.1:
                pygame.draw.circle(self.background, color, (random.randint(0, res.x), random.randint(0,res.y)), 1, 0)
            else:
                self.background.set_at((random.randint(0, res.x), random.randint(0,res.y)), color)
        self.signal_spot = V2(res.x - 280, 65)
        self.jumps = []
        while len(self.jumps) < 20:
            pt = V2(random.randint(res.x // 8, res.x * 7 // 8), random.randint(100, res.y - 110))
            nearest,dist = get_nearest_pos(pt, self.jumps)
            if dist > 40 ** 2:
                self.jumps.append(pt)
        self.jumps.sort(key=lambda j:j.x / 4 + j.y, reverse=True)
        self.initial_spot = V2(280, res.y - 80)
        self.jumps.append(self.signal_spot)
        self.time = 0
        self.signal_data = [(0,0,0)]
        self.current_signal_freq = 0
        self.current_signal_mag = 0
        for i in range(60):
            if random.random() < 0.25:
                self.signal_data.append((random.random() + 0.3, random.random(),random.random()))
            else:
                self.signal_data.append(self.signal_data[-1])

        self.current_path = [V2(self.initial_spot)]
        self.current_path_pt = V2(self.initial_spot)
        self.path_flashing = False
        self.path_flash_time = 0

        self.readout_text = open(resource_path("assets/readout.txt")).read()
        self.readout_line = 0
        self.readout_time = -8
        self._generate_image(0.05)

    def _generate_image(self,dt):
        self.image = self.background.copy()

        res = game.Game.inst.game_resolution

        ## GRID ##
        grid_t = 0.5#(self.time / 6) % 1
        for i in range(int(grid_t * 32), int(res.x), 32):
            pygame.draw.line(self.image, PICO_LIGHTGRAY, (i, 0), (i, res.y), 1)
        for i in range(int(grid_t * 32), int(res.y), 32):
            pygame.draw.line(self.image, PICO_LIGHTGRAY, (0, i), (res.x, i), 1)


        ## JUMPS ##
        jumps_t = clamp(self.time / 2 - 2.5,0,1)
        jumps_i = int(jumps_t * len(self.jumps))

        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        for i,jump in enumerate(self.jumps):
            if i < jumps_i:
                xg = (jump.x - 16) // 32 * 32 + 16
                yg = (jump.y - 16) // 32 * 32 + 16
                x_grid = int((jump.x - 16) // 32)
                y_grid = int((jump.y - 16) // 32)
                pygame.draw.rect(self.image, PICO_BLUE, (xg+2,yg+2,33,33), 1)
                text.render_multiline_to(self.image, (xg + 4, yg-2), "%s%d" % (letters[x_grid % 26], y_grid), 'tiny', PICO_BLUE)

        for i,jump in enumerate(self.jumps[0:jumps_i]):
            #poly = [V2(-1, -1), V2(1, -1), V2(1,1), V2(-1,1)]
            #poly = [helper.from_angle(p.as_polar()[1] + self.time / 2 + i) * 5 + jump for p in poly]
            width = 1
            if jump in self.current_path:
                width = 0
            #pygame.draw.polygon(self.image, PICO_GREEN, [p for p in poly], width)
            pygame.draw.circle(self.image, PICO_BLACK, jump, 3, width)

        
        ## DISTRESS SIGNAL ##
        signal_t = self.time % 1
        pygame.draw.circle(self.image, PICO_WHITE, self.signal_spot, 5, 0)
        signal_circle_color = PICO_WHITE
        if signal_t > 0.66:
            signal_circle_color = PICO_GREEN
        pygame.draw.circle(self.image, signal_circle_color, self.signal_spot, 5 + signal_t * 19, 1)

        radar_t = (self.time / 4) % 1
        #pygame.draw.circle(self.image, PICO_GREEN, self.initial_spot, radar_t * 500, 1)

        ## SHIP ##
        poly = [self.initial_spot + V2(0, -6), self.initial_spot + V2(6, 6), self.initial_spot + V2(-6, 6)]
        pygame.draw.polygon(self.image, PICO_GREEN, [tuple(p) for p in poly], 0)            

        ## READOUT ##
        self.readout_time += dt
        if self.readout_time > 1.25:
            self.readout_time = -1
            self.readout_line = random.randint(0,220)

        if self.readout_time > 0:
            readout_end = int(self.readout_line + self.readout_time * 13)
            lines = [l.strip() for l in self.readout_text.split("\n")][self.readout_line:readout_end]            
            text.render_multiline_to(self.image, (5,5), "\n".join(lines), "tiny", PICO_LIGHTGRAY, wrap_width=300, center=False)
            pygame.draw.line(self.image, PICO_LIGHTGRAY, (2,2), (2,self.readout_time * 230 // 10 * 10 + 2))

        ## TOP ##
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,0,res.x,35), 0)

        ## WAVEFORM ##
        wave_x = res.x - 210 - 10
        m_t = math.cos(clamp(self.time,0,1) * 3.14159) * -0.5 + 0.5
        msg_rect = (wave_x, 10, 210, 80 * m_t)
        pygame.draw.rect(self.image, PICO_BROWN, msg_rect, 0)
        pygame.draw.rect(self.image, PICO_YELLOW, msg_rect, 1)
        if self.time > 1:
            pts = []
            adj = 0.1
            msg_index = int((self.time * 10) % len(self.signal_data))
            signal_freq, signal_mag, extra = self.signal_data[msg_index]
            self.current_signal_mag = signal_mag * adj + self.current_signal_mag * (1 - adj)
            self.current_signal_freq = signal_freq * adj + self.current_signal_freq * (1 - adj)
            for x in range(0, 200, 1):
                dx = x ** (extra / 2 + 1)
                mag = self.current_signal_mag
                if extra < 0.3:
                    mag = math.cos(x * extra * 0.1)
                if extra > 0.9:
                    mag = 3
                y = clamp(math.sin(dx * 0.25 * self.current_signal_freq + self.time * 15 + signal_freq) * 35 * mag + 50,15,85)
                pts.append((int(res.x - 210 - 5 + x),int(y)))
            pygame.draw.lines(self.image, PICO_YELLOW, False, pts, 1)
        text.render_multiline_to(self.image, (wave_x + 5, 14), "SIGNAL", "small", PICO_YELLOW)

        ## PATH ##
        if self.time > 6:
            delta = self.current_path_pt - self.current_path[-1]
            if delta.length_squared() < 4 ** 2:
                jumps_left = list(set([tuple(p) for p in self.jumps]) - set([tuple(p) for p in self.current_path]))
                nearest = nearest_order_pos(self.current_path_pt, jumps_left)[0:4]
                if nearest:
                    random.shuffle(nearest)
                    self.current_path.append(V2(nearest[0]))

            color = PICO_GREEN
            if self.path_flashing:
                self.path_flash_time -= dt
                if (self.path_flash_time * 4) % 1 >0.5:
                    color = PICO_DARKGREEN
            else:
                towards = self.current_path[-1] - self.current_path_pt
                dist = towards.length()
                self.current_path_pt += helper.try_normalize(towards) * 200 * dt / clamp(((dist / 50) + 0.25), 0.15, 2)

            lines = self.current_path[0:-1] + [V2(self.current_path_pt)]
            
            if color == PICO_GREEN:
                #pygame.draw.lines(self.image, color, False, [tuple(p) for p in lines], 2)
                done = False
                i = 1
                pt = V2(self.current_path[0])
                while not done:
                    towards = (self.current_path[i] - pt)
                    if towards.length_squared() < 8 ** 2:
                        pt  = V2(self.current_path[i])
                        i += 1
                        
                    if i >= len(self.current_path) - 1:
                        towards = (self.current_path_pt - pt)
                        if towards.length_squared() < 8 ** 2:
                            done = True
                            break

                    towards = (self.current_path[i] - pt)

                    pt += helper.try_normalize(towards) * 5
                    #pygame.draw.circle(self.image, color, pt, 1, 0)
                    pygame.draw.rect(self.image, color, (pt.x - 1, pt.y - 1, 2, 2), 0)

            if len(self.current_path) > 7 and not self.path_flashing:
                self.path_flashing = True
                self.path_flash_time = 1

            if self.path_flashing and self.path_flash_time < 0:
                self.path_flashing = False
                self.current_path = [V2(self.initial_spot)]
                self.current_path_pt = V2(self.initial_spot)

        ## INDICATOR ##
        p1 = self.signal_spot + V2(1, -1) * 5
        p2 = self.signal_spot + V2(1,-1) * (45 - m_t * 30) + V2(0,1)
        p3 = V2(wave_x, p2.y)
        pygame.draw.line(self.image, PICO_YELLOW, tuple(p1), tuple(p2))
        pygame.draw.line(self.image, PICO_YELLOW, tuple(p2), tuple(p3))

        btn_t = clamp((self.time - 3.5) * 2, 0, 1)
        ## BUTTONS ##
        if btn_t > 0:
            pygame.draw.rect(self.image, PICO_WHITE, (res.x // 4 - 2, res.y // 2 - 50 - 2, res.x // 2 + 4, 104))
            color = PICO_BLACK
            if btn_t < 0.25:
                color = PICO_WHITE
            pygame.draw.rect(self.image, color, (res.x // 4, res.y // 2 - 50, res.x // 2, 100))

        ## VIGNETTE ##
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,0,res.x,res.y), 4)
            

    def update(self, dt):
        self.time += dt
        self._generate_image(dt)
        return super().update(dt)
