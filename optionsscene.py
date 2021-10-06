import math
import random
import sys

import pygame

import controlsscene
import creditsscene
import framesprite
import game
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


class OptionsScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.ignore_next_resize_event = False

        self.selected_item_index = 0
        
        self.items = {}

        x = self.game.game_resolution.x / 2 - 120
        y = self.game.game_resolution.y / 2 - 120

        if not self.game.save.get_setting("fullscreen"):
            self.game.make_resizable(True)


        self.menumanager = menu.Menu(self, V2(x,y))
        self.setup_menu()

        self.sm = states.Machine(states.UIEnabledState(self))

    def setup_menu(self):
        self.menumanager.clear()
        available_resolutions = self.game.get_available_resolutions()
        resolutions = ["%dx%d" % res for res in available_resolutions]
        is_fullscreen = self.game.save.get_setting("fullscreen")
        fullscreen_word = "YES" if is_fullscreen else "NO"
        fres = self.game.save.get_setting("resolution")
        current_resolution = "%dx%d" % tuple(fres)        
        self.menumanager.add_option(menu.ButtonMenuOption("BACK", self.click_back))
        self.menumanager.add_option(menu.ButtonMenuOption("JOYSTICK CONTROLS", self.click_controls))
        self.menumanager.add_option(menu.SliderMenuOption("MUSIC", 0, 10, self.game.save.get_setting("music_volume"), self.music_change))
        self.menumanager.add_option(menu.SliderMenuOption("SOUND", 0, 10, self.game.save.get_setting("sound_volume"), self.sound_change))
        self.menumanager.add_option(menu.ChoiceMenuOption("FULL SCREEN", ['YES', 'NO'], fullscreen_word, self.fullscreen_change))
        if is_fullscreen:
            self.menumanager.add_option(menu.ChoiceMenuOption("RESOLUTION", resolutions, current_resolution, self.resolution_change))        

    def on_display_resize(self, size):
        if self.ignore_next_resize_event:
            self.ignore_next_resize_event = False
            return
        self.adjust_resolution(size)
        return super().on_display_resize(size)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()

    def click_back(self):
        self.game.make_resizable(False)
        self.game.set_scene("menu")

    def music_change(self, value):
        self.game.save.set_setting("music_volume", value)
        self.game.save.save()
        sound.update_volume()        

    def sound_change(self, value):
        changed = self.game.save.get_setting("sound_volume") != value
        self.game.save.set_setting("sound_volume", value)    
        self.game.save.save()
        sound.update_volume() 
        if changed:
            sound.play("laser1")        

    def fullscreen_change(self, value):
        fs = value == "YES"
        self.game.save.set_setting("fullscreen", fs)
        if fs:
            self.adjust_resolution(V2(*self.game.get_available_resolutions()[0]))
            self.game.make_resizable(False)
        else:
            self.adjust_resolution(V2(1200, 720))
            self.game.make_resizable(True)
            self.ignore_next_resize_event = True
        
        x = self.game.game_resolution.x / 2 - 120
        y = self.game.game_resolution.y / 2 - 120        
        self.menumanager.pos = V2(x,y)
        self.setup_menu()
        self.game.save.save()

    def resolution_change(self, value):
        if not self.game.save.get_setting("fullscreen"):
            return
        reso = V2(*[int(s) for s in value.split("x")])
        self.adjust_resolution(reso)

    def adjust_resolution(self, resolution):
        self.game.menu_bg_cache_obj = None
        self.game.save.set_setting("resolution", resolution.tuple_int())
        fs = self.game.save.get_setting("fullscreen")
        self.game.set_resolution(resolution, fs, resizable = not fs)
        x = self.game.game_resolution.x / 2 - 120
        y = self.game.game_resolution.y / 2 - 120        
        self.menumanager.reconstruct(V2(x,y))
        self.game.save.save()

    def click_controls(self):
        self.game.make_resizable(False)
        self.game.scene = controlsscene.ControlsScene(self.game)
        self.game.scene.start()                        

    def take_input(self, inp, event):
        self.menumanager.take_input(inp, event)
        if inp == "back" or inp == "menu":
            self.click_back()
        return super().take_input(inp, event)
