import pygame
import scene
import states
from colors import *

from intel import intelpanel, intelstate


class IntelScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        s = intelstate.IntelStateBase(self)
        s.on_back = self.on_back
        self.sm = states.Machine(s)

    def update(self, dt):
        for spr in self.ui_group.sprites():
            spr.update(dt)
        return super().update(dt)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()

    def on_back(self):
        self.game.set_scene("menu")
