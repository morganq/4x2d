import math
import sys

import creditsscene
import framesprite
import game
import menuscene
import pygame
import save
import scene
import simplesprite
import sound
import states
import text
from colors import *
from resources import resource_path
from run import RunInfo
from slider import Slider
from starmap import starmapscene
from v2 import V2

from tutorial.tutorial1scene import Tutorial1Scene
from tutorial.tutorialmessage import TutorialMessage


class IntroScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.sm = states.Machine(states.UIEnabledState(self))
        self.bg = simplesprite.SimpleSprite(V2(0,0), "assets/intro1.png")
        self.background_group.add(self.bg)
        self.stage = 0

        self.time = 0

    def update(self, dt):
        self.time += dt

        for s in self.ui_group.sprites():
            s.update(dt)

        if self.time > 1 and self.stage == 0:
            self.stage += 1
            self.tut = TutorialMessage("")
            self.tut.set_text("The Federation rules the universe with an iron fist. Humanity is the only known civilization that has refused to collaborate...")
            self.tut.pos = V2(game.RES[0] / 2 - 172, game.RES[1] - 54)
            self.tut._reposition_children()
            self.ui_group.add(self.tut)
            self.tut.add_all_to_group(self.ui_group)
            self.tut.set_visible(True)
            self.tut.fade_in()

        if self.time > 10 and self.stage == 1:
            self.stage += 1
            self.tut.set_visible(False)
            self.bg.image = pygame.image.load(resource_path("assets/intro2.png"))

        if self.time > 11 and self.stage == 2:
            self.stage += 1
            self.tut.set_text("Chased from Earth, we were scattered to the stars.")
            self.tut.set_visible(True)
            self.tut.fade_in()

        if self.time > 16 and self.stage == 3:
            self.stage += 1
            self.tut.set_text("If we could find allies across the universe, we could band together and take back our home!")
            self.tut.set_visible(True)
            self.tut.fade_in()            

        if self.time > 23 and self.stage == 4:
            self.stage += 1
            self.bg.image = pygame.image.load(resource_path("assets/intro3.png"))
            self.tut.set_visible(False)

        if self.time > 24 and self.stage == 5:
            self.stage += 1
            self.tut.set_visible(True)
            self.tut.fade_in()
            self.tut.set_text("Commander - A distress signal - it’s other humans!")

        if self.time > 29 and self.stage == 6:
            self.stage += 1
            self.tut.set_text("Standing between us and the others are many hostile Federation star systems, and our oxygen is running out...")

        if self.time > 36 and self.stage == 7:
            self.stage += 1
            self.tut.set_text("But - this is our chance! ONWARDS!")

        if self.time > 42:
            self.game.scene = Tutorial1Scene(self.game)
            self.game.scene.start()

        super().update(dt)

    def take_input(self, inp, event):
        if inp == "menu":
            self.game.scene = menuscene.MenuScene(self.game)
            self.game.scene.start()
        return super().take_input(inp, event)

    def render(self):
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()
