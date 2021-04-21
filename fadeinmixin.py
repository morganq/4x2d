import pygame
import math
import colors
import random

class FadeInMixin:
    def fade_in(self, speed=1, fade_mode=None):
        if not hasattr(self, "_original_update"): self._original_update = self.update
        if not hasattr(self, "fade_mode"): self.fade_mode = fade_mode or "diag_wipe"
        self._fade_speed = speed
        if hasattr(self, "_fade_time") and self._fade_time != 0:
            self._fade_direction = 1
            return
        self._fade_complete_image = self.image
        self.image = pygame.Surface(self._fade_complete_image.get_size(), pygame.SRCALPHA)
        
        self.update = self._fade_update
        self.paused_update = self._fade_update
        self._fade_time = 0
        self._fade_direction = 1
        self.visible = 1

    def fade_out(self, speed=1, fade_mode=None):
        if not hasattr(self, "_original_update"): self._original_update = self.update        
        if not hasattr(self, "fade_mode"): self.fade_mode = fade_mode or "diag_wipe"
        self._fade_speed = speed
        if hasattr(self, "_fade_time") and self._fade_time != 0:
            self._fade_direction = -1
            return
        self._fade_complete_image = self.image
        self.update = self._fade_update
        self._fade_time = 0
        self._fade_direction = -1
        self.visible = 1

    def _noise(self, t):
        w,h = self._fade_complete_image.get_size()
        self.image = pygame.Surface(self._fade_complete_image.get_size(), pygame.SRCALPHA)
        for i in range(500):
            x = random.randint(0, w-1)
            y = random.randint(0, h-1)
            c = self._fade_complete_image.get_at((x,y))
            if c[3] > 0:
                if random.random() > 0.5:
                    bx = random.randint(1,int(t * 30 + 1))
                    pygame.draw.rect(self.image, c, (x, y, bx, bx), 0)
                    #self.image.set_at((x,y), c)

    def _diag_wipe(self, t):
        w,h = self._fade_complete_image.get_size()
        self.image = pygame.Surface(self._fade_complete_image.get_size(), pygame.SRCALPHA)
        self.image.blit(self._fade_complete_image, (0,0))
        n = (1-t) * (w + h + 4) - h - 4
        points = [(-h,0), (n + h, 0), (n, h), (-h,h)]
        pygame.draw.polygon(self.image, (0,0,0,0), points)
        pygame.draw.line(self.image, colors.PICO_PINK, (n + h, 0), (n, h))
        pygame.draw.line(self.image, (0,0,0,0), (n + h + 2, 0), (n + 2, h))
        pygame.draw.line(self.image, (0,0,0,0), (n + h + 4, 0), (n + 4, h))

    def _fade_update(self, dt):
        self._original_update(dt)
        self._fade_time = min(self._fade_time + dt * self._fade_speed, 1)
        t = min(math.cos(self._fade_time * 3.14159) * -0.5 + 0.51, 1)
        if self._fade_direction < 0:
            t = 1 - t
        
        if self.fade_mode == "diag_wipe":
            self._diag_wipe(t)
        elif self.fade_mode == "noise":
            self._noise(t)
        else:
            self.image = self._fade_complete_image

        if self._fade_direction == 1 and t >= 1:
            self.update = self._original_update
            self.image = self._fade_complete_image
            self._fade_complete()
            self._fade_time = 0

        if self._fade_direction == -1 and t <= 0:
            self.update = self._original_update
            self.image = self._fade_complete_image
            self.visible = 0            
            self._fade_time = 0
        
    def _fade_complete(self):
        pass