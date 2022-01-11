import pygame

import game
import resources
import spritebase
import text
from colors import PICO_BLACK, PICO_DARKBLUE, PICO_WHITE
from fadeinmixin import FadeInMixin
from helper import clamp
import pygame
V2 = pygame.math.Vector2


class Panel(spritebase.SpriteBase, FadeInMixin):
    def __init__(self, pos, panel_for):
        spritebase.SpriteBase.__init__(self, pos)
        self.panel_for = panel_for
        self._controls = []
        self.padding = 9
        self.layer = 10
        self._background_offset = V2(0,0)

        self.tab = None

    def set_visible(self, value):
        self.visible = value
        for ci in self._controls:
            ci['control'].visible = value

    def position_nicely(self, scene):
        if self.panel_for:
            x = self.panel_for.x - self._width / 2
            y = self.panel_for.y - self._height / 2
            if x > game.Game.inst.game_resolution.x / 2:
                x = self.panel_for.x - self.panel_for._width / 2 - self._width - 10
            else:
                x = self.panel_for.x + self.panel_for._width / 2 + 10
            y = clamp(y, 2, game.Game.inst.game_resolution.y - self._height - 2 - 40)
        else:
            x = game.Game.inst.game_resolution.x / 2 - self._width / 2
            y = game.Game.inst.game_resolution.y / 2 - self._height / 2
        self.pos = V2(x,y)
        self._reposition_children()

    def kill(self):
        for ci in self._controls:
            ci['control'].kill()
        spritebase.SpriteBase.kill(self)

    def add(self, control, pos):
        control.layer = self.layer + 1
        self._controls.append({'control':control,'pos':pos})

    def remove(self, control):
        self._controls = [c for c in self._controls if c['control'] != control]

    def empty(self):
        for c in self._controls:
            c['control'].kill()
        self._controls = []

    def get_control_of_type(self, klass):
        try:
            return self.get_controls_of_type(klass)[0]
        except IndexError:
            return None

    def get_controls_of_type(self, klass):
        return [c['control'] for c in self._controls if isinstance(c['control'], klass)]      

    def add_all_to_group(self, group):
        group.add(self)
        for ci in self._controls:
            group.add(ci['control'])

    def _reposition_children(self):
        for ci in self._controls:
            control = ci['control']
            pos = ci['pos']
            control.x = pos.x + self.x + self._background_offset.x
            control.y = pos.y + self.y + self._background_offset.y

    def redraw(self):
        xmin, xmax, ymin, ymax = 0,0,0,0
        outerpad = 3
        for ci in self._controls:
            control = ci['control']
            pos = ci['pos']
            xmax = max(pos.x + control.width, xmax)
            ymax = max(pos.y + control.height, ymax)

        tab_width = 0
        if self.tab:
            icon_offset = 0
            icon = None
            if 'icon' in self.tab:
                icon = pygame.image.load(resources.resource_path(self.tab['icon']))
                icon_offset = icon.get_width() + 4

            tab_foreground = PICO_BLACK
            if sum(self.tab['color']) < 90 * 3:
                tab_foreground = PICO_WHITE
            tab_text = text.render_multiline(self.tab['text'], 'small', tab_foreground)
            tab_width = tab_text.get_size()[0] + 8 + icon_offset            
        
        box_width = xmax + self.padding * 2
        box_height = ymax + self.padding * 2

        tab_offset = 0
        if self.tab:
            tab_offset = 14

        total_height = box_height + tab_offset
        self.image = pygame.Surface((box_width, box_height + tab_offset), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PICO_DARKBLUE, (outerpad,outerpad + tab_offset, box_width - outerpad * 2, box_height - outerpad * 2), 0)
        self._width = box_width
        self._height = box_height + tab_offset
#        pygame.draw.rect(self.image, PICO_WHITE, (0, tab_offset, 1, box_height), 1)

        if self.tab:        
            pygame.draw.rect(self.image, self.tab['color'], (outerpad, outerpad, tab_width, tab_offset), 0)
 #           pygame.draw.rect(self.image, PICO_WHITE, (0, 0, 1, tab_offset + 1), 1)
            if 'icon' in self.tab:
                self.image.blit(icon, (4 + outerpad,4 + outerpad))
            self.image.blit(tab_text, (4 + icon_offset + outerpad, 4 + outerpad))

        self._background_offset = V2(self.padding, self.padding + tab_offset)

        pygame.draw.line(self.image, PICO_WHITE, (0,0), (4,0))
        pygame.draw.line(self.image, PICO_WHITE, (0,0), (0,4))
        pygame.draw.line(self.image, PICO_WHITE, (box_width - 4, total_height-1), (box_width, total_height-1))
        pygame.draw.line(self.image, PICO_WHITE, (box_width - 1, total_height-4), (box_width - 1, total_height))

        self._reposition_children()
        self._recalc_rect()

    def fade_in(self, speed=10, fade_mode="noise"):
        for ci in self._controls:
            control = ci['control']
            control.visible = False
        return super().fade_in(speed=speed, fade_mode=fade_mode)

    def _fade_complete(self):
        for ci in self._controls:
            control = ci['control']
            if control.image:
                control.visible = True
