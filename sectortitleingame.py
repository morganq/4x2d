import math

import pygame

import spritebase
import text
from colors import *
from constants import REWARD_ICON_WIDTH, REWARD_ICONS_ORDER
from helper import clamp
from resources import resource_path

V2 = pygame.math.Vector2


class SectorTitleInGame(spritebase.SpriteBase):
    def __init__(self, pos, sector_title, reward_name):
        super().__init__(pos)
        self.sector_title = sector_title
        self.reward_name = reward_name
        self.icon_sheet = pygame.image.load(resource_path("assets/reward_icons.png")).convert_alpha()
        if self.reward_name:
            self._generate_image()
        else:
            self._generate_image_noreward()
        self.initial_pos = self.pos
        self.target_pos = V2(self.pos.x, 8)
        self.t = 0

    def _generate_image(self):
        ts1 = text.render_multiline(self.sector_title, "small", PICO_BLUE)
        ts2 = text.render_multiline("Reward:", "small", PICO_BLUE)
        tw = ts1.get_width() + ts2.get_width() + 16
        self.image = pygame.Surface((tw + REWARD_ICON_WIDTH - 1, REWARD_ICON_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,3,self.image.get_width(),self.image.get_height()-6), 0)
        self.image.blit(ts1, (4,8))
        self.image.blit(ts2, (ts1.get_width() + 18,8))
        w = REWARD_ICON_WIDTH
        h = REWARD_ICON_WIDTH
        x = w * REWARD_ICONS_ORDER[self.reward_name]
        self.image.blit(self.icon_sheet, (self.image.get_width() - REWARD_ICON_WIDTH - 1, 0), (x,0,w,h))
        self._width, self._height = self.image.get_size()
        self._recalc_rect()

    def _generate_image_noreward(self):
        ts1 = text.render_multiline(self.sector_title, "small", PICO_BLUE)
        tw = ts1.get_width() + 16
        self.image = pygame.Surface((tw, REWARD_ICON_WIDTH), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,3,self.image.get_width(),self.image.get_height()-6), 0)
        self.image.blit(ts1, (tw // 2 - ts1.get_width() // 2,8))
        self._width, self._height = self.image.get_size()
        self._recalc_rect()

    def update(self, dt):
        self.t = clamp(self.t + dt * 0.85, 0, 1)
        zt = math.cos(self.t * 3.14159) * -0.5 + 0.5
        zt = zt ** 1.25
        self.pos = V2(self.initial_pos.x, self.initial_pos.y * (1-zt) + self.target_pos.y * zt)
        return super().update(dt)
