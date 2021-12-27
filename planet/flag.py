import framesprite
import pygame
from colors import *


class Flag(framesprite.FrameSprite):
    def __init__(self, pos, color):
        super().__init__(pos, sprite_sheet="assets/flag.png", frame_width=17)
        self._base_sheet = self._sheet
        self.offset = (0.5, 1)
        self.time = 0
        self.set_color(color)

    def set_color(self, color):
        if not self._base_sheet:
            self._base_sheet = self._sheet.copy()
        outline_mask = pygame.mask.from_surface(self._base_sheet, 127)
        surf = outline_mask.to_surface(setcolor=(*PICO_BLACK,255), unsetcolor=(0,0,0,0))      

        color_mask = pygame.mask.from_threshold(self._base_sheet, (*PICO_RED,255), (2,2,2,255))
        surf2 = color_mask.to_surface(setcolor=(*color,255), unsetcolor=(0,0,0,0))
        surf.blit(surf2,(0,0))

        white_mask = pygame.mask.from_threshold(self._base_sheet, (*PICO_WHITE,255), (2,2,2,255))
        surf3 = white_mask.to_surface(setcolor=(*PICO_WHITE,255), unsetcolor=(0,0,0,0))
        surf.blit(surf3,(0,0))

        self._sheet = surf

        self._update_image()        

    def update(self, dt):
        self.time += dt
        ft = int(self.time * 9)
        if ft <= 12:
            self.frame = ft
        if ft > 12:
            self.frame = (ft+1) % 7 + 6
        if self.time > 4:
            self.kill()
        return super().update(dt)
