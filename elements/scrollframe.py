import pygame
import spritebase
from colors import *
from helper import clamp


class VScrollFrame(spritebase.SpriteBase):
    def __init__(self, pos, surf, height=300):
        super().__init__(pos)
        self.base_surf = surf
        self.frame_height = height
        self._scroll_y = 0
        self.last_mouse_pos = None
        self.selectable = True
        self._generate_image()

    def _generate_image(self):
        pad = 25
        self._width = self.base_surf.get_width()
        self._height = self.frame_height + pad * 2
        frame = self.base_surf.subsurface((0, self._scroll_y, self._width, self.frame_height))
        self.image = pygame.Surface((self._width, self.height))
        self.image.fill(PICO_DARKBLUE)
        self.image.blit(frame, (0, pad))

        def draw_triangle(x, y, color, invert=False):
            yd = 1
            if invert: yd = -1
            p1 = (x - 6, y + yd * -5)
            p2 = (x + 6, y + yd * -5)
            p3 = (x, y + yd * 7)
            pygame.draw.polygon(self.image, color, [p1,p2,p3], 0)


        color = PICO_WHITE
        if self._scroll_y <= 0:
            color = PICO_DARKGRAY
        for i in range(3):
            draw_triangle(self._width // 2 - 30 + 30 * i, pad // 2, color, True)
        color = PICO_WHITE
        if self._scroll_y >= self.get_max_scroll():
            color = PICO_DARKGRAY
        for i in range(3):
            draw_triangle(self._width // 2 - 30 + 30 * i, self._height - pad // 2, color, False)            

        self._recalc_rect()

    def update(self, dt):
        if self.last_mouse_pos:
            if (
                self.last_mouse_pos.x > self._width * 0.2 and 
                self.last_mouse_pos.x < self._width * 0.8 and 
                self.last_mouse_pos.y < 25
            ):
                self._scroll_y = clamp(self._scroll_y - dt * 150, 0, self.get_max_scroll())
                self._generate_image()

            if (
                self.last_mouse_pos.x > self._width * 0.2 and 
                self.last_mouse_pos.x < self._width * 0.8 and 
                self.last_mouse_pos.y > self.frame_height + 25
            ):
                self._scroll_y = clamp(self._scroll_y + dt * 150, 0, self.get_max_scroll())     
                self._generate_image()           

        return super().update(dt)

    def get_max_scroll(self):
        return self.base_surf.get_height() - self.frame_height

    def on_mouse_move(self, pos):
        self.last_mouse_pos = pos - self.pos
        return super().on_mouse_move(pos)
    
    def on_mouse_exit(self, pos):
        self.last_mouse_pos = None
        return super().on_mouse_exit(pos)
