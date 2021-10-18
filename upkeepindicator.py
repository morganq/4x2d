import pygame

import spritebase
from colors import *
from text import render_multiline_to
from v2 import V2

DEFAULT_WIDTH = 120

class UpkeepIndicator(spritebase.SpriteBase):
    def __init__(self, scene):
        pos = scene.meters['gas'].pos + V2(scene.meters['gas'].width, scene.meters['gas'].height + 1)
        super().__init__(pos)
        self.scene = scene
        self.has_upkeep = False
        self.upkeep_time = 0

    def _generate_image(self):
        delta = self.scene.meters['gas'].width - DEFAULT_WIDTH
        self._width = max(delta, 200)
        self._height = 20
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        blink = True
        if self.upkeep_time < 1:
            blink = ((self.upkeep_time * 4) % 1) > 0.5
        if delta > 0 and not self.scene.cinematic and blink:
            pygame.draw.line(self.image, PICO_YELLOW, (0, 0), (0, 1), 1)
            pygame.draw.line(self.image, PICO_YELLOW, (0, 1), (delta-1, 1), 1)
            pygame.draw.line(self.image, PICO_YELLOW, (delta-1, 0), (delta-1, 1), 1)
            pygame.draw.line(self.image, PICO_YELLOW, (delta / 2 - 1, 3), (delta / 2 + 2, 6), 1)
            render_multiline_to(self.image, (delta / 2 + 4, 3), "Large Fleet Upkeep", "tiny", PICO_YELLOW)

    def update(self, dt):
        if not self.has_upkeep and self.scene.meters['gas'].width > DEFAULT_WIDTH:
            self.has_upkeep = True
        if self.has_upkeep and self.scene.meters['gas'].width <= DEFAULT_WIDTH:
            self.has_upkeep = False
        if self.has_upkeep:
            self.upkeep_time += dt
        self._generate_image()
        return super().update(dt)
