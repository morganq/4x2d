import pygame
from simplesprite import SimpleSprite

class FrameSprite(SimpleSprite):
    type = None
    def __init__(self, pos, sheet, frame_width):
        SimpleSprite.__init__(self, pos, sheet)
        self._sheet_width = self._width
        self._sheet = self.image
        self._frame = 0
        self._frame_width = frame_width
        self._width = self._frame_width
        self._update_image()
        self.rect = pygame.Rect(0,0,self._width,self._height)
        self._num_frames = self._sheet_width // self._frame_width

    def _update_image(self):
        if self._sheet:
            self.image = self._sheet.subsurface(
                self._frame * self._frame_width, 0,
                self._frame_width, self._height)

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, frame):
        self._frame = frame
        self._update_image()