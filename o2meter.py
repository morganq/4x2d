import spritebase
from resources import resource_path
import pygame
from helper import clamp

O2_MAX = 3600
class O2Meter(spritebase.SpriteBase):
    def __init__(self, pos):
        super().__init__(pos)
        self.full_image = pygame.image.load(resource_path("assets/o2-full.png")).convert_alpha()
        self.empty_image = pygame.image.load(resource_path("assets/o2-empty.png")).convert_alpha()
        self.o2 = O2_MAX
        self.blink_time = 0

        self._generate_image()

    def _generate_image(self):
        self.image = self.full_image.copy()
        pxs = (1 - (clamp(self.o2,0, O2_MAX) / O2_MAX)) * 60 + 5
        self.image.blit(self.empty_image, (0,0), (0, 0, pxs, self.image.get_height()))

    def update(self, dt):
        if self.o2 <= 0:
            self.blink_time += dt
            if self.blink_time % 1 > 0.5:
                self.visible = True
            else:
                self.visible = False
        return super().update(dt)