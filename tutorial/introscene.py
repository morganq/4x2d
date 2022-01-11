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
import upscale
from colors import *
from resources import resource_path
from run import RunInfo
from slider import Slider
from starmap import starmapscene
import pygame
V2 = pygame.math.Vector2

from tutorial.tutorial1scene import Tutorial1Scene
from tutorial.tutorialmessage import TutorialMessage

tut_stage_times = [
    1,
    10,
    11,
    16,
    23,
    24,
    29,
    36,
    42,
    99
]

class IntroScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.sm = states.Machine(states.UIEnabledState(self))
        self.bg = simplesprite.SimpleSprite(self.game.game_offset, "assets/intro-sm-1.png")
        self.bg.image = upscale.pixel(self.bg.image, 4)
        self.bg.pos = V2(self.game.game_resolution.x /2 - self.bg.image.get_width() / 2, self.game.game_resolution.y /2 - self.bg.image.get_height() / 2)
        self.background_group.add(self.bg)
        self.mockup = text.Text("Mockup Art", "big", V2(30,30))
        self.ui_group.add(self.mockup)
        self.stage = 0

        self.time = 0
        self.tutorial_speed = 1
        self.tut = TutorialMessage("")
        self.tut.pos = V2(self.game.game_resolution.x / 2 - 172, self.game.game_resolution.y - 54)
        self.tut._reposition_children()
        self.ui_group.add(self.tut)
        self.tut.add_all_to_group(self.ui_group)    
        self.tut.set_visible(False)    

    def update(self, dt):
        self.time += dt * self.tutorial_speed

        for s in self.ui_group.sprites():
            s.update(dt)

        if self.time > tut_stage_times[0] and self.stage == 0:
            self.stage += 1
            self.tut.set_text("The Federation rules the universe with an iron fist. Humanity is the only known civilization that has refused to collaborate...")
            self.tut.set_visible(True)
            self.tut.fade_in()

        if self.time > tut_stage_times[1] and self.stage == 1:
            self.stage += 1
            self.tut.set_visible(False)
            self.bg.image = upscale.pixel(pygame.image.load(resource_path("assets/intro-sm-2.png")),4)

        if self.time > tut_stage_times[2] and self.stage == 2:
            self.stage += 1
            self.tut.set_text("Chased from Earth, we were scattered to the stars.")
            self.tut.set_visible(True)
            self.tut.fade_in()

        if self.time > tut_stage_times[3] and self.stage == 3:
            self.stage += 1
            self.tut.set_text("If we could find allies across the universe, we could band together and take back our home!")
            self.tut.set_visible(True)
            self.tut.fade_in()           

        if self.time > tut_stage_times[4] and self.stage == 4:
            self.stage += 1
            self.bg.image = upscale.pixel(pygame.image.load(resource_path("assets/intro-sm-3.png")),4)
            self.tut.set_visible(False)

        if self.time > tut_stage_times[5] and self.stage == 5:
            self.stage += 1
            self.tut.set_visible(True)
            self.tut.fade_in()
            self.tut.set_text("Commander - A distress signal - it’s other humans!")

        if self.time > tut_stage_times[6] and self.stage == 6:
            self.stage += 1
            self.tut.set_text("Standing between us and the others are many hostile Federation star systems, and our oxygen is limited...")

        if self.time > tut_stage_times[7] and self.stage == 7:
            self.stage += 1
            self.tut.set_text("But - this is our chance! ONWARDS!")

        if self.time > tut_stage_times[8] and self.stage == 8:
            self.game.scene = Tutorial1Scene(self.game)
            self.game.scene.start()

        super().update(dt)

    def take_input(self, inp, event):
        if inp == "menu":
            self.game.scene = menuscene.MenuScene(self.game)
            self.game.scene.start()
        if self.tut:
            if inp == "confirm" or inp == "action" or inp == "click":
                if self.tut.done:
                    #self.stage += 1
                    if self.stage <= len(tut_stage_times):
                        self.time = tut_stage_times[self.stage]
                else:
                    self.tutorial_speed = 1
                    self.tut.speed = 10
                print(self.stage, self.time)

        return super().take_input(inp, event)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()
