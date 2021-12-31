import pygame

import game
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
        self.add(t, V2(0,17))
        
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


class Tooltippable:
    def setup(self, title, body, tooltip_position="bottom"):
        self._tooltip_title = title
        self._tooltip_body = body
        self._tooltip_panel = None
        self._tooltip_enabled = True
        self._tooltip_position = tooltip_position
        self.on("mouse_enter", self._tooltip_mouse_enter)
        self.on("mouse_exit", self._tooltip_mouse_exit)
        self.on("mouse_down", self._tooltip_mouse_down)
    
    def teardown(self):
        if self._tooltip_panel:
            self._tooltip_panel.kill()        

    def _tooltip_mouse_enter(self, *args):
        if not self._tooltip_enabled:
            return
            
        # I don't remember why we'd need to do this... I guess to update/refresh tooltip
        if self._tooltip_panel:
            self._tooltip_panel.kill()

        self._tooltip_panel = TooltipPanel(self._tooltip_title, self._tooltip_body)

        if self._tooltip_position == "side":
            if self._tooltip_panel.width + self.pos.x + 30 > game.Game.inst.game_resolution.x:
                self._tooltip_panel.pos = self.pos + V2(-5 - self._tooltip_panel.width,0)
            else:
                self._tooltip_panel.pos = self.pos + V2(30,0)
            if self._tooltip_panel.height + self._tooltip_panel.y > game.Game.inst.game_resolution.y:
                self._tooltip_panel.pos = (self._tooltip_panel.pos.x, game.Game.inst.game_resolution.y - self._tooltip_panel.height)

        elif self._tooltip_position == "bottom":
            x = int(-self._tooltip_panel.width / 2 + self.width / 2)
            self._tooltip_panel.pos = self.pos + V2(x,24)

        self._tooltip_panel._reposition_children()
        self.groups()[0].add(self._tooltip_panel)
        self._tooltip_panel.add_all_to_group(self.groups()[0])

    def _tooltip_mouse_exit(self, *args):
        if self._tooltip_panel:
            self._tooltip_panel.kill()

    def _tooltip_mouse_down(self, *args):
        if self._tooltip_panel:
            self._tooltip_panel.kill()        
