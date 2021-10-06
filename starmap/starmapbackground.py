import random

import game
import pygame
import spritebase
from colors import *


class StarmapBackground(spritebase.SpriteBase):
    def __init__(self, pos, rewards_width = 100):
        super().__init__(pos)
        self.rewards_width = rewards_width
        self.center_y = round(game.Game.inst.game_resolution.y * 3 / 5)
        self._generate_image()


    def _generate_image(self):
        res = game.Game.inst.game_resolution
        self._width, self._height = res.tuple()

        self.image = pygame.Surface(res.tuple_int(), pygame.SRCALPHA)
        self.image.fill(PICO_BLACK) 

        x = game.Game.inst.game_offset.x
        lx = x + 360

        pygame.draw.rect(self.image, PICO_DARKGREEN, (0,0,lx, self.center_y))
        pygame.draw.rect(self.image, PICO_DARKBLUE, (lx,0,res.x-lx, self.center_y))
        pygame.draw.line(self.image, PICO_DARKBLUE, (lx-2,0), (lx-2, self.center_y))

        for i in range(200):
            color = PICO_LIGHTGRAY
            if random.random() < 0.25:
                color = PICO_WHITE
            
            if random.random() < 0.1:
                pygame.draw.circle(self.image, color, (random.randint(0, res.x), random.randint(0,self.center_y)), 1, 0)
            else:
                self.image.set_at((random.randint(0, res.x), random.randint(0,self.center_y)), color)

        y = self.center_y

        poly = [
            (res.x / 2 - self.rewards_width/2 + 4, y-8),
            (res.x / 2 + self.rewards_width/2 + 4, y-8),
            (res.x / 2 + self.rewards_width/2 - 4, y+8),
            (res.x / 2 - self.rewards_width/2 - 4, y+8),
        ]

        pygame.draw.polygon(self.image, PICO_BLUE, poly, 0)
        pygame.draw.polygon(self.image, PICO_WHITE, poly, 1)
