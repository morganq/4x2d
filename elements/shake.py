import math

import pygame
import spritebase
from helper import clamp
from v2 import V2


class Shake(spritebase.SpriteBase):
    def __init__(self, scene, pos, radius, time = 0.5):
        self.scene = scene
        super().__init__(pos)
        self.radius = radius
        self.end_time = time
        self.time = 0
        self.offset = (0.5, 0.5)
        self.mask1 = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.mask1.fill((0,0,0,0))
        pygame.draw.circle(self.mask1, (255,255,255,255), (self.radius, self.radius), self.radius, 0)
        self.layer = 1000
        self.intensity = 1.5
        if self.radius > 15:
            self.intensity = 3

    def _generate_image(self):
        pad = 4
        amt = math.sin(clamp(self.time / self.end_time, 0, 1) * 3.14159) * self.intensity
        self._width = self._height = self.radius * 2 + pad * 2
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        x = int(self.x)
        y = int(self.y)        
        src1 = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        src1.blit(self.scene.game.screen, (0,0), (x - self.radius, y - self.radius, self.radius * 2, self.radius * 2))
        src1.blit(self.mask1, (0,0), None, pygame.BLEND_RGBA_MULT)
        offset = V2(pad, pad) + V2.random_angle() * amt
        self.image.blit(src1, offset.tuple_int())
        self._recalc_rect()

    def render(self, screen):
        self._generate_image()
        screen.blit(self.image, self.rect)

    def update(self, dt):
        self.time += dt
        return super().update(dt)

def shake(scene, pos, radius, time=0.5):
    s = Shake(scene, pos, radius, time)
    scene.shake_sprite = s
