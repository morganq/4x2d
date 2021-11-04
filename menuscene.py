import math
import random
import sys

import pygame

import controlsscene
import creditsscene
import framesprite
import game
import hqlogo
import menu
import menubackground
import newgamescene
import save
import scene
import simplesprite
import sound
import states
import text
import tutorial.introscene
from colors import *
from helper import clamp
from run import RunInfo
from slider import Slider
from starmap import starmapscene
from v2 import V2


class Parallaxed:
    def __init__(self, obj, degree):
        self.obj = obj
        self.degree = degree
        self.end_pos = self.obj.pos

    def update(self, time):
        t = clamp(time / 3.5, 0, 1)
        tz = (math.cos(t * 3.14159) * -0.5 + 0.5) ** 0.5
        delta = V2(0, 300) * self.degree * (1-tz)
        self.obj.pos = self.end_pos + delta

class MenuScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.parallax = []
        self.stars = []
        for i in range(120):
            s = framesprite.FrameSprite(V2(random.randint(0, self.game.game_resolution.x),random.randint(-30, self.game.game_resolution.y)), "assets/bgstar.png", 11)
            s.frame = 4 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.05))
            self.stars.append(s)
        for i in range(60):
            s = framesprite.FrameSprite(V2(random.randint(0, self.game.game_resolution.x),random.randint(-60, self.game.game_resolution.y)), "assets/bgstar.png", 11)
            s.frame = 2 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.1))   
            self.stars.append(s)         
        for i in range(20):
            s = framesprite.FrameSprite(V2(random.randint(0, self.game.game_resolution.x),random.randint(-100, self.game.game_resolution.y)), "assets/bgstar.png", 11)
            s.frame = 0 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.2)) 
            self.stars.append(s)           

        if self.game.menu_bg_cache_obj:
            self.bg = self.game.menu_bg_cache_obj
            self.bg.pos = V2(-80, 40)
        else:
            self.bg = menubackground.MenuBackground(V2(-80,40), True)
            self.game.menu_bg_cache_obj = self.bg

        
        self.background_group.add(self.bg)
        self.parallax.append(Parallaxed(self.bg, 1))

        self.logo = hqlogo.HQLogo(V2(self.game.game_resolution.x / 2,25))
        self.logo.offset = (0.5, 0)
        self.game_group.add(self.logo)

        self.selected_item_index = 0
        
        self.items = {}

        x = 340 * (self.game.game_resolution.x / game.RES[0])
        y = self.game.game_resolution.y / 2 - 50
        self.menumanager = menu.Menu(self, V2(x,y))
        if self.game.save.run_state:
            jumps = len(self.game.save.run_state['path'])-1
            if jumps == 1:
                continue_text = "CONTINUE (1 jump)"
            else:
                continue_text = "CONTINUE (%d jumps)" % jumps
            self.menumanager.add_option(menu.ButtonMenuOption(continue_text, self.click_continue))
        self.menumanager.add_option(menu.ButtonMenuOption("NEW GAME", self.click_new))
        self.menumanager.add_option(menu.ButtonMenuOption("TUTORIAL", self.click_tutorial))
        self.menumanager.add_option(menu.ButtonMenuOption("MULTIPLAYER", self.click_multiplayer))
        self.menumanager.add_option(menu.ButtonMenuOption("OPTIONS", self.click_options))
        self.menumanager.add_option(menu.ButtonMenuOption("EXIT", sys.exit))

        self.time = 0

        self.sm = states.Machine(states.UIEnabledState(self))

    def update(self, dt):
        self.time += min(dt,0.1)
        self.bg.update(dt)
        for para in self.parallax:
            para.update(self.time)

        for spr in self.game_group.sprites():
            spr.update(dt)

        for i in range(10):
            s = random.choice(self.stars)
            s.frame = int(s.frame / 2) * 2 + random.randint(0,1)
        super().update(dt)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game.screen.blit(self.bg.wobble_image, self.bg.pos.tuple_int())
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()    

    def click_multiplayer(self):
        self.game.set_scene("multiplayer_menu")

    def click_tutorial(self):
        self.game.scene = tutorial.introscene.IntroScene(self.game)
        self.game.scene.start()

    def click_options(self):
        self.game.set_scene("options")

    def click_continue(self):
        self.game.run_info = self.game.save.get_run_state()
        self.game.scene = starmapscene.StarMapScene(self.game)
        self.game.scene.start()        

    def click_new(self):
        self.game.scene = newgamescene.NewGameScene(self.game)
        self.game.scene.start()                                  

    def take_input(self, inp, event):
        self.menumanager.take_input(inp, event)
        return super().take_input(inp, event)
