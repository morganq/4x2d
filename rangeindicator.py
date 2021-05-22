import pygame
from spritebase import SpriteBase
from v2 import V2

class RangeIndicator(SpriteBase):
    def __init__(self, pos, radius, color, line_length=2, line_space=2):
        super().__init__(pos)
        self.radius = radius
        self.color = color
        self.line_length = line_length
        self.line_space = line_space
        self.angle = 0
        self._offset = (0.5, 0.5)
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        num_lines = int(self.radius * 6.2818 / (self.line_space + self.line_length))
        for i in range(num_lines):
            a = i / num_lines * 6.2818 + self.angle
            pc = V2(self.radius, self.radius) + V2.from_angle(a) * self.radius
            p1 = pc + V2.from_angle(a + 3.14159 / 2) * self.line_length / 2
            p2 = pc - V2.from_angle(a + 3.14159 / 2) * self.line_length / 2
            pygame.draw.line(self.image, self.color, p1.tuple(), p2.tuple(), 1)

        self._width = self.radius * 2
        self._height = self._width
        self._recalc_rect()

    def update(self, dt):
        #self.angle += dt / 12
        #self._generate_image()
        return super().update(dt)
