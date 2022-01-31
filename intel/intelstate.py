import levelstates
import pygame
from helper import clamp
from states import UIEnabledState

from intel import intelpanel


class IntelStateBase(UIEnabledState):
    def enter(self):
        self.panel = intelpanel.IntelPanel(pygame.Vector2(0,0), None, self.on_back)
        self.panel.position_nicely(self.scene)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.hover_filter = self.filter_only_panel_ui
        self.scroll_y_value = 0
        return super().enter()

    def joy_scroll(self, dt):
        sf = self.panel.scroll_frame
        sf._scroll_y = clamp(sf._scroll_y + dt * 150 * self.scroll_y_value, 0, sf.get_max_scroll())
        sf._generate_image()

    def update(self, dt):
        self.joy_scroll(dt)
        return super().update(dt)

    def paused_update(self, dt):
        self.joy_scroll(dt)
        return super().paused_update(dt)

    def take_input(self, input, event):
        if input == "joymotion":
            if abs(event['delta'].y) > 0.5:
                self.scroll_y_value = event['delta'].y
            else:
                self.scroll_y_value = 0
        if input == "back":
            self.on_back()
        return super().take_input(input, event)

class IntelState(IntelStateBase):
    def __init__(self, scene):
        super().__init__(scene)

    def enter(self):
        self.scene.paused = True
        return super().enter()

    def on_back(self):
        self.scene.sm.transition(levelstates.PauseState(self.scene))

    def exit(self):
        self.panel.kill()
        return super().exit()
