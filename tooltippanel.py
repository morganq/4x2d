import pygame

from colors import *
from panel import Panel
from text import Text
from v2 import V2


class TooltipPanel(Panel):
    def __init__(self, title, description):
        Panel.__init__(self, (5,5), None)
        self.layer = 13
        t = Text(title, "small", (0,0), PICO_WHITE, False, multiline_width=500)
        t.layer = 14
        self.add(t, V2(0,0))
        t = Text(description, "small", (0,0), PICO_LIGHTGRAY, False, multiline_width=160, center=False)
        t.layer = 14
        t._height -= 4
        self.add(t, V2(0,15))
        
        self.bump_out = 0
        self.max_bump = 3
        self.redraw()

    def _reposition_children(self):
        for ci in self._controls:
            control = ci['control']
            pos = ci['pos']
            control.x = pos.x + self.x + self._background_offset.x + self.max_bump - self.bump_out
            control.y = pos.y + self.y + self._background_offset.y + self.max_bump - self.bump_out

    def redraw(self):
        xmin, xmax, ymin, ymax = 0,0,0,0        
        for ci in self._controls:
            control = ci['control']
            pos = ci['pos']
            xmax = max(pos.x + control.width, xmax)
            ymax = max(pos.y + control.height, ymax)

        box_width = xmax + self.padding * 2
        box_height = ymax + self.padding * 2
        full_width = box_width + self.max_bump
        full_height = box_height + self.max_bump

        self.image = pygame.Surface((full_width, full_height), pygame.SRCALPHA)
        if self.bump_out < 1:
            color = PICO_BLUE
        else:
            color = PICO_DARKBLUE
        pygame.draw.rect(self.image, PICO_WHITE, (self.max_bump, self.max_bump, box_width, box_height))
        pygame.draw.rect(self.image, color, (self.max_bump - self.bump_out, self.max_bump - self.bump_out, box_width, box_height), 0)
        pygame.draw.line(self.image, PICO_WHITE, (self.max_bump - self.bump_out,self.max_bump - self.bump_out), (self.max_bump - self.bump_out + 4,self.max_bump - self.bump_out))
        pygame.draw.line(self.image, PICO_WHITE, (self.max_bump - self.bump_out,self.max_bump - self.bump_out), (self.max_bump - self.bump_out,self.max_bump - self.bump_out + 4))
        self._background_offset = V2(self.padding, self.padding)
        self._width = full_width
        self._height = full_height
        self._reposition_children()
        self._recalc_rect()

    def update(self, dt):
        if self.bump_out < self.max_bump:
            self.bump_out = min(self.bump_out + dt * 22, self.max_bump)
            self.redraw()
        return super().update(dt)
