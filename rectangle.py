import pygame

import spritebase


class Rectangle(spritebase.SpriteBase):
    def __init__(self, pos, size, color):
        super().__init__(pos)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        self.image.fill(color)
