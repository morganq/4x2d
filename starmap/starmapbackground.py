import random

import game
import pygame
import spritebase
from colors import *


class StarmapBackground(spritebase.SpriteBase):
    def __init__(self, pos, rewards_width = 100):
        super().__init__(pos)
        self.rewards_width = rewards_width
        self._generate_image()


    def _generate_image(self):
        res = game.Game.inst.game_resolution
        self._width, self._height = res.tuple()

        self.image = pygame.Surface(res.tuple_int(), pygame.SRCALPHA)
        self.image.fill(PICO_BLACK) 

        pygame.draw.rect(self.image, PICO_DARKGREEN, (0,0,res.x, res.y-180))
        pygame.draw.rect(self.image, PICO_DARKBLUE, (360,0,res.x-360, res.y-180))
        pygame.draw.line(self.image, PICO_DARKBLUE, (358,0), (358, res.y-180))

        for i in range(200):
            color = PICO_LIGHTGRAY
            if random.random() < 0.25:
                color = PICO_WHITE
            
            if random.random() < 0.1:
                pygame.draw.circle(self.image, color, (random.randint(0, res.x), random.randint(0,res.y-180)), 1, 0)
            else:
                self.image.set_at((random.randint(0, res.x), random.randint(0,res.y-180)), color)

        y = 220

        poly = [
            (res.x / 2 - self.rewards_width/2 + 4, y-8),
            (res.x / 2 + self.rewards_width/2 + 4, y-8),
            (res.x / 2 + self.rewards_width/2 - 4, y+8),
            (res.x / 2 - self.rewards_width/2 - 4, y+8),
        ]

        pygame.draw.polygon(self.image, PICO_BLUE, poly, 0)
        pygame.draw.polygon(self.image, PICO_WHITE, poly, 1)
