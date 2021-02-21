import framesprite
import pygame
from v2 import V2

class Particle(framesprite.FrameSprite):
    def __init__(self, sheet, width, pos, time, vel=None):
        # They can provide a list of colors and we'll make a 1-pixel particle out of them
        if isinstance(sheet, list):
            colors = sheet
            sheet = pygame.Surface((len(colors), 1), pygame.SRCALPHA)
            for i,color in enumerate(colors):
                sheet.set_at((i, 0), color)
                
        framesprite.FrameSprite.__init__(self, pos, sheet, width)
        self.time = time
        self.initial_time = time
        self.vel = vel or V2(0,0)
        self.type = "particle"
        self._layer = 1

    def update(self, dt):
        self.time -= dt
        self.pos += self.vel * dt
        i = int((1 - self.time / self.initial_time) * self._num_frames)
        if self.time <= 0:
            self.kill()
        else:        
            self.frame = i
