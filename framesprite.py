import pygame
from resources import resource_path
from simplesprite import SimpleSprite

class FrameSprite(SimpleSprite):
    type = None
    def __init__(self, pos, sprite_sheet = None, frame_width = None):
        SimpleSprite.__init__(self, pos)
        self._frame = 0
        if sprite_sheet:
            self.set_sprite_sheet(sprite_sheet, frame_width=frame_width)

    def set_sprite_sheet(self, sprite_sheet, frame_width = None):
        if isinstance(sprite_sheet, str):
            self._sheet = pygame.image.load(resource_path(sprite_sheet)).convert_alpha()
        else:
            self._sheet = sprite_sheet
        self._sheet_width = self._sheet.get_width()
        
        self._frame_width = frame_width or 0
        if self._frame_width == 0:
            if self._sheet: # If no frame width, it should just be the image width.
                self._frame_width = self._sheet.get_width()
            else: # No image, this is invisible
                self._frame_width = 1
        self._width = self._frame_width
        self._recalc_rect()
        self._num_frames = self._sheet_width // self._frame_width
        self._frame = self._frame % self._num_frames
        self._update_image()

    def _update_image(self):
        if self._sheet:
            self.image = self._sheet.subsurface(
                self._frame * self._frame_width, 0,
                self._frame_width, self._height)
        else:
            self.image = pygame.Surface((1,1), pygame.SRCALPHA)

    @property
    def frame(self):
        return self._frame

    @frame.setter
    def frame(self, frame):
        self._frame = frame
        self._update_image()