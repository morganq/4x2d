import math

import pygame

import game
import text
import upgrade
from button import Button
from colors import *
from helper import clamp, nearest_order
from simplesprite import SimpleSprite
from slider import Slider
from spritebase import SpriteBase
from v2 import V2


class JoystickCursor(SpriteBase):
    def __init__(self, scene, pos):
        super().__init__(V2(0,0))
        self.cursor_pos = pos
        self.nearest_obj = None
        self.hovering = None
        self.joystick_state = V2(0,0)
        self.scene = scene
        self.options_text = text.Text("", "small", V2(0,0), PICO_PINK, multiline_width=200, center=False)
        self.scene.ui_group.add(self.options_text)
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface((game.RES[0], game.RES[1]), pygame.SRCALPHA)

        pygame.draw.circle(self.image, PICO_PINK, self.cursor_pos.tuple(), 7, 1)
        pygame.draw.circle(self.image, PICO_WHITE, self.cursor_pos.tuple(), 2, 0)

        if self.nearest_obj:
            rect = (
                self.nearest_obj.apparent_pos.x - self.nearest_obj.radius - 4,
                self.nearest_obj.apparent_pos.y - self.nearest_obj.radius - 4,
                self.nearest_obj.radius * 2 + 8,
                self.nearest_obj.radius * 2 + 8
            )
            delta = (self.cursor_pos - self.nearest_obj.apparent_pos)
            dist, ang = V2(delta.x, -delta.y).to_polar()
            pygame.draw.arc(self.image, PICO_PINK, rect, ang - 1, ang + 1)

            if dist > 15:
                dn = delta.normalized()
                p1 = self.cursor_pos - dn * 7
                p2 = self.nearest_obj.apparent_pos + dn * (self.nearest_obj.radius + 4)
                pygame.draw.line(self.image, PICO_PINK, p1.tuple(), p2.tuple(), 1)

        self._width, self._height = game.RES

    def joystick_delta(self, delta):
        self.joystick_state = delta

    def set_nearest(self, obj):
        self.nearest_obj = obj
        self.update_hover()

    def update(self, dt):
        self.cursor_pos += self.joystick_state * dt * 350
        self.scene.game.last_joystick_pos = self.cursor_pos
        self.options_text.pos = self.cursor_pos + V2(8, -8)
        self._generate_image()
        return super().update(dt)

    def kill(self):
        if self.hovering and self.hovering.alive():
            self.hovering.on_mouse_exit(self.hovering.pos)
        self.options_text.kill()
        super().kill()

    def update_hover(self):
        if self.hovering and self.hovering.alive() and self.hovering != self.nearest_obj:
            self.hovering.on_mouse_exit(self.hovering.pos)
        if self.nearest_obj:
            self.hovering = self.nearest_obj
            self.hovering.on_mouse_enter(self.hovering.pos)

    def set_button_options(self, options):
        if options:
            self.options_text.set_text("\n".join(options))
        else:
            self.options_text.set_text("")


class JoystickPanelCursor(SpriteBase):
    def __init__(self, scene, controls):
        super().__init__(V2(0,0))
        self.controls = controls
        self.control_pos = (0,0)
        self.scene = scene
        self.joystick_state = V2(0,0)        
        self.last_dir = None
        self.hovering = None
        self.update_hover()
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface((game.RES[0], game.RES[1]), pygame.SRCALPHA)

        c = self.get_current_control()
        rect = (
            c.x - 4,
            c.y - 4,
            c.width + 8,
            c.height + 8
        )
        #pygame.draw.rect(self.image, PICO_PINK, rect, 1)
        pygame.draw.line(self.image, PICO_PINK, (c.x - 2, c.y), (c.x - 2, c.y + c.height))

        self._width, self._height = game.RES

    def kill(self):
        if self.hovering and self.hovering.alive():
            self.hovering.on_mouse_exit(self.hovering.pos)
        super().kill()

    def get_current_control(self):
        return self.controls[self.control_pos[1]][self.control_pos[0]]

    def press(self, dir):
        c = self.get_current_control()
        if dir == "down":
            y = min(self.control_pos[1] + 1, len(self.controls) - 1)
            x = clamp(self.control_pos[0], 0, len(self.controls[y]) - 1)
            self.control_pos = (x, y)
            self.update_hover()
            self._generate_image()
        elif dir == "up":
            y = max(self.control_pos[1] - 1, 0)
            x = clamp(self.control_pos[0], 0, len(self.controls[y]) - 1)            
            self.control_pos = (x, y)
            self.update_hover()
            self._generate_image()
        if dir == "left":
            if isinstance(c, Slider):
                c.set_value(c.value - 1)
            else:
                x = max(self.control_pos[0] - 1, 0)
                y = self.control_pos[1]
                self.control_pos = (x, y)
                self.update_hover()
                self._generate_image()
        if dir == "right":
            if isinstance(c, Slider):
                c.set_value(c.value + 1)
            else:
                y = self.control_pos[1]                
                x = min(self.control_pos[0] + 1, len(self.controls[y]) - 1)
                self.control_pos = (x, y)
                self.update_hover()
                self._generate_image()

    def update_hover(self):
        if self.hovering and self.hovering.alive() and self.get_current_control() != self.hovering:
            self.hovering.on_mouse_exit(self.hovering.pos)
        self.hovering = self.get_current_control()
        self.hovering.on_mouse_enter(self.hovering.pos)

    def confirm(self):
        c = self.get_current_control()
        if isinstance(c, Button) or isinstance(c, text.Text) or isinstance(c, upgrade.upgradebutton.UpgradeButton):
            c.on_mouse_down(c.pos)

    def joystick_delta(self, delta):
        self.joystick_state = delta
        if delta.sqr_magnitude() > 0.75 ** 2:
            _,ang = delta.to_polar()
            ang /= math.pi / 2
            ang4 = round(ang)
            angs = {0:"right", 1:"down", 2:"left", -2:"left", -1:"up"}
            dir = angs[ang4]
            if dir != self.last_dir:
                self.last_dir = dir
                self.press(dir)
        else:
            self.last_dir = None

    def update(self, dt):
        return super().update(dt)
