from collections import defaultdict

import pygame

import text
from colors import *
from helper import clamp
from resources import resource_path
from spritebase import SpriteBase

ORDER = ['fighter', 'scout', 'bomber', 'interceptor', 'battleship', 'other']

EXPAND_TIME = 0.5

class CivShipUI(SpriteBase):
    def __init__(self, pos, civ):
        super().__init__(pos)
        self.civ = civ
        self.images = {n : pygame.image.load(resource_path("assets/i-%s.png" % n)) for n in ORDER}
        self._percent_o2_use = pygame.image.load(resource_path("assets/percent_o2_use.png"))
        self.expand_timer = 0
        self.target_y = self.pos.y

    def _generate_image(self):
        w = 65
        h = 74 + self.expand_timer * 15
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        self.image.fill(PICO_BLACK)
        pygame.draw.rect(self.image, PICO_DARKGREEN, (1,1,w - 2, h - 2), 1)
        ships = self.civ.get_all_combat_ships()
        data = defaultdict(lambda : 0)
        for s in ships:
            name = s['name']
            if name not in ORDER:
                name = 'other'
            data[name] += 1
        for i,name in enumerate(ORDER):
            x = i % 2 * 30 + 5
            y = (i // 2) * 19 + 15
            img = self.images[name]
            color = PICO_GREEN
            
            if data[name] <= 0:
                color = PICO_DARKGRAY
                color_mask = pygame.mask.from_threshold(img, (*PICO_GREEN,255), (2,2,2,255))
                img = color_mask.to_surface(setcolor=(*color,255), unsetcolor=(0,0,0,0))
                
            self.image.blit(img, (x,y + 2))
            text.render_multiline_to(self.image, pygame.Vector2(x + 16, y), str(data[name]), "tiny", color)

        color = PICO_LIGHTGRAY
        upkeep = int(self.civ.get_fleet_o2_upkeep(len(ships)) * 100)
        if upkeep >= 100:
            color = PICO_RED
        elif upkeep >= 50:
            color = PICO_ORANGE
        elif upkeep > 0:
            color = PICO_YELLOW
        pygame.draw.rect(self.image, color, (3, 3, w - 6, 10), 0)
        shipstext = text.render_multiline("SHIPS: %d" % len(ships), "tiny", PICO_BLACK)
        self.image.blit(shipstext, (6, 0))

        if self.expand_timer >= 1:
            pygame.draw.rect(self.image, color, (3, h - 13, w - 6, 10), 0)
            s = text.render_multiline("+%d" % upkeep, "tiny", PICO_BLACK)
            self.image.blit(s, pygame.Vector2(6, h - 16))
            self.image.blit(self._percent_o2_use, (6 + s.get_width() - 2, h - 11))

        self._width, self._height = w,h
        self._recalc_rect()

    def update(self, dt):
        if len(self.civ.get_all_combat_ships()) >= self.civ.get_fleet_soft_cap():
            self.expand_timer = clamp(self.expand_timer + dt / EXPAND_TIME, 0, 1)
        else:
            self.expand_timer = clamp(self.expand_timer - dt / EXPAND_TIME, 0, 1)
        self._generate_image()
        self.y = self.y * 0.5 + self.target_y * 0.5
        return super().update(dt)
