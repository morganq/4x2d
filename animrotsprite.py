import pygame

from framesprite import FrameSprite
from resources import resource_path


class AnimRotSprite(FrameSprite):
    def __init__(self, pos, sprite_sheet=None, frame_width=0):
        self._angle = 0
        self.debug_rotation_num = 0
        FrameSprite.__init__(self, pos, sprite_sheet=sprite_sheet, frame_width=frame_width)

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_image()

    def _update_image(self):
        if not self._sheet:
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)
            return
            
        sw = self._sheet.get_width()
        h = self._sheet.get_height()
        midframe = (sw / self._frame_width) // 2

        rotation_number = round((self._angle) / 6.2818 * 8) % 8
        self.debug_rotation_num = rotation_number
        diagonal = (rotation_number % 2) == 1

        sheet_frame = self._frame + midframe if diagonal else self._frame
        rect = (sheet_frame * self._frame_width, 0, self._frame_width, h)
        image = self._sheet.subsurface(*rect)
        rotation = rotation_number // 2
        self.image = pygame.transform.rotate(image, -rotation * 90)
        self._width = self._frame_width
        self._height = h
        self._recalc_rect()
        
