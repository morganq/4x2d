import pygame
import resources
import spritebase
from colors import *


class Flash(spritebase.SpriteBase):
    def __init__(self, target, speed = 3):
        super().__init__(target.pos)
        self.speed = speed
        self.target = target
        self.offset = tuple(target.offset[::])
        self.layer = target.layer + 1
        self.time = 0
        self.dither_image = pygame.image.load(resources.resource_path("assets/dither_white.png")).convert_alpha()
        self._generate_image()
        
    def _generate_image(self):
        self.image = pygame.Surface(self.target.image.get_size(), pygame.SRCALPHA)
        if self.time < 0.5:
            self.image.fill(PICO_WHITE)
        else:
            self.image.blit(self.dither_image, (0,0))
        self._width = self.target._width
        self._height = self.target._height
        outline_mask = pygame.mask.from_surface(self.target.image, 127)
        mask = outline_mask.to_surface(setcolor=(*PICO_WHITE,255), unsetcolor=(0,0,0,0))   
        self.image.blit(mask, (0,0), None, pygame.BLEND_RGBA_MULT)
        self._recalc_rect()           

    def update(self, dt):
        self.time += dt * self.speed
        if self.time > 1:
            self.kill()
        self._generate_image()
        return super().update(dt)

def flash_sprite(target, speed=3):
    spr = Flash(target, speed=speed)
    #target.groups()[0].add(spr)
    target.scene.ui_group.add(spr)
