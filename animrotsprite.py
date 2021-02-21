from spritebase import SpriteBase
import pygame
from resources import resource_path

class AnimRotSprite(SpriteBase):
    def __init__(self, pos, sheet, frame_width):
        SpriteBase.__init__(self, pos)
        self._sheet = pygame.image.load(resource_path(sheet)).convert_alpha()
        self._frame_width = frame_width
        self._frame = 0
        self._angle = 0
        self._update_image()

    def _update_image(self):
        sw = self._sheet.get_width()
        h = self._sheet.get_height()
        midframe = (sw / self._frame_width) // 2

        sixteenth = 6.2818 / 16
        rotation_number = int((self._angle - sixteenth) / 6.2818 * 8) % 8
        diagonal = (rotation_number % 2) == 1

        sheet_frame = self._frame + midframe if diagonal else self._frame
        rect = (sheet_frame * self._frame_width, 0, self._frame_width, h)
        image = self._sheet.subsurface(*rect)
        rotation = rotation_number // 2
        self.image = pygame.transform.rotate(image, -rotation * 90)
        self._width = self._frame_width
        self._height = h
        self._recalc_rect()
        
