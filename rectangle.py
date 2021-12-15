import pygame

import spritebase


class Rectangle(spritebase.SpriteBase):
    def __init__(self, pos, size, color, line_width=0):
        super().__init__(pos)
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        if line_width > 0:
            pygame.draw.rect(self.image, color, (0,0,size[0]-1,size[1]-1), line_width)
        else:
            self.image.fill(color)
