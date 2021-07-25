import math
import sys

import pygame

import controlsscene
import creditsscene
import framesprite
import game
import save
import scene
import simplesprite
import sound
import states
import text
import tutorial.introscene
from colors import *
from run import RunInfo
from slider import Slider
from starmap import starmapscene
from v2 import V2


class MenuState(states.UIEnabledState):
    is_basic_joystick_panel = True  

    def get_joystick_cursor_controls(self):
        controls = []
        if self.scene.items['continue'].selectable:
            controls.append([self.scene.items['continue']])
        controls.append([self.scene.items['new']])
        controls.append([self.scene.items['tutorial']])
        controls.append([self.scene.items['controls']])
        controls.append([self.scene.music_meter])
        controls.append([self.scene.sound_meter])
        controls.append([self.scene.items['resolution']])
        controls.append([self.scene.items['credits']])
        controls.append([self.scene.items['exit']])
        return controls

class MenuScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        bg = simplesprite.SimpleSprite(V2(0,0), "assets/menubg.png")
        self.background_group.add(bg)

        self.selected_item_index = 0
        
        self.items = {}

        y = 45
        dy = 35
        self.items['continue'] = text.Text("CONTINUE", "small", V2(320, y), multiline_width=200, onhover=lambda v:self.onhover(0,v), onclick=self.click_continue)
        if self.game.save.run_state:
            jumps = len(self.game.save.run_state['path'])-1
            if jumps == 1:
                self.items['continue'].set_text("CONTINUE (%d jump)" % jumps)
            else:
                self.items['continue'].set_text("CONTINUE (%d jumps)" % jumps)
        else:
            self.items['continue'].visible = False
            self.items['continue'].selectable = False
        self.items['new'] = text.Text("NEW GAME", "small", V2(320, y + dy * 1), onhover=lambda v:self.onhover(1,v), onclick=self.click_new)
        self.items['tutorial'] = text.Text("TUTORIAL", "small", V2(320, y + dy * 2), onhover=lambda v:self.onhover(2,v), onclick=self.click_tutorial)
        self.items['controls'] = text.Text("CONTROLS", "small", V2(320, y + dy * 3), onhover=lambda v:self.onhover(3,v), onclick=self.click_controls)
        self.items['music'] = text.Text("MUSIC", "small", V2(320, y + dy * 4))
        self.items['sound'] = text.Text("SOUND", "small", V2(320, y + dy * 5))
        self.items['resolution'] = text.Text("RESOLUTION", "small", V2(320, y + dy * 6), onhover=lambda v:self.onhover(6,v), onclick=self.click_resolution)
        self.items['credits'] = text.Text("CREDITS", "small", V2(320, y + dy * 7), onhover=lambda v:self.onhover(7,v))
        self.items['exit'] = text.Text("EXIT", "small", V2(320, y + dy * 8), onhover=lambda v:self.onhover(8,v), onclick=sys.exit)
        
        self.item_names = list(self.items.keys())

        for item in self.items.values():
            self.ui_group.add(item)
        self.update_selection()

        self.music_meter = Slider(V2(370, y + dy * 4), 100, 0, 10, onchange=self.music_change)
        self.ui_group.add(self.music_meter)
        self.sound_meter = Slider(V2(370,  y + dy * 5), 100, 0, 10, onchange=self.sound_change)
        self.ui_group.add(self.sound_meter)        
        self.resolution_display = text.Text("1x1", "small", (400,  y + dy * 6))
        self.ui_group.add(self.resolution_display)
        self.update_settings()
        #sound.play_music("overworld")

        self.time = 0

        self.sm = states.Machine(MenuState(self))

    def onhover(self, item, value):
        if value:
            self.selected_item_index = item
            self.update_selection()

    def update(self, dt):
        self.time += dt
        super().update(dt)

    def render(self):
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()

    def music_change(self, value):
        self.game.save.set_setting("music_volume", value)
        self.update_settings()
        sound.update_volume()        

    def sound_change(self, value):
        changed = self.game.save.get_setting("sound_volume") != value
        self.game.save.set_setting("sound_volume", value)    
        self.update_settings()
        sound.update_volume() 
        if changed:
            sound.play("laser1")        

    def click_resolution(self):
        self.game.save.set_setting("scale", (self.game.save.get_setting("scale")) % 3 + 1)
        self.update_settings()
        self.game.update_scale(self.game.save.get_setting("scale"))

    def click_tutorial(self):
        self.game.scene = tutorial.introscene.IntroScene(self.game)
        self.game.scene.start()

    def click_continue(self):
        self.game.run_info = self.game.save.get_run_state()
        self.game.scene = starmapscene.StarMapScene(self.game)
        self.game.scene.start()        

    def click_new(self):
        self.game.run_info = RunInfo()
        self.game.scene = starmapscene.StarMapScene(self.game)
        self.game.scene.start()             

    def click_controls(self):
        self.game.scene = controlsscene.ControlsScene(self.game)
        self.game.scene.start()                        

    def update_selection(self):
        for key, item in self.items.items():
            if key == self.item_names[self.selected_item_index]:
                item.color = PICO_GREEN
                item.set_text(item._text)
            else:
                item.color = PICO_WHITE
                item.set_text(item._text)

    def update_settings(self):
        mw = self.game.save.get_setting("music_volume")
        sw = self.game.save.get_setting("sound_volume")
        self.music_meter.set_value(mw)
        self.sound_meter.set_value(sw)

        scale = self.game.save.get_setting("scale")
        self.resolution_display.set_text("%d x %d" % (game.RES[0] * scale, game.RES[1] * scale))

        self.game.save.save()

    def take_input_keyboard(self, inp, event):
        if inp == "down":
            self.selected_item_index = min(self.selected_item_index + 1, 5)
            self.update_selection()
        elif inp == "up":
            self.selected_item_index = max(self.selected_item_index - 1, 0)
            self.update_selection()
        elif inp == "right":
            if self.item_names[self.selected_item_index] == 'music':
                self.game.save.set_setting("music_volume", min(self.game.save.get_setting("music_volume") + 1, 10))
                self.update_settings()
                sound.update_volume()
            if self.item_names[self.selected_item_index] == 'sound':
                self.game.save.set_setting("sound_volume", min(self.game.save.get_setting("sound_volume") + 1, 10))                
                self.update_settings()
                #sound.play("step0")
            if self.item_names[self.selected_item_index] == 'resolution':
                self.game.save.set_setting("scale", min(self.game.save.get_setting("scale") + 1, 5))
                self.update_settings()
                self.game.update_scale(self.game.save.get_setting("scale"))
        elif inp == "left":
            if self.item_names[self.selected_item_index] == 'music':
                self.game.save.set_setting("music_volume", max(self.game.save.get_setting("music_volume") - 1, 0))
                self.update_settings()            
                sound.update_volume()
            if self.item_names[self.selected_item_index] == 'sound':
                self.game.save.set_setting("sound_volume", max(self.game.save.get_setting("sound_volume") - 1, 0))
                self.update_settings()
                #sound.play("step0")
            if self.item_names[self.selected_item_index] == 'resolution':
                self.game.save.set_setting("scale", max(self.game.save.get_setting("scale") - 1, 1))
                self.update_settings()            
                self.game.update_scale(self.game.save.get_setting("scale"))    
        elif inp == "action":
            if self.item_names[self.selected_item_index] == 'start':
                #sound.play("step0")
                self.game.return_to_map()
            if self.item_names[self.selected_item_index] == 'exit':
                sys.exit()
            if self.item_names[self.selected_item_index] == 'credits':
                self.game.scene = creditsscene.CreditsScene(self.game)
                self.game.scene.start()
