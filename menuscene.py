import math
import random
import sys

import pygame

import controlsscene
import creditsscene
import framesprite
import game
import menubackground
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

        self.bg = menubackground.MenuBackground(V2(-80,40), True)
        self.background_group.add(self.bg)
        self.parallax.append(Parallaxed(self.bg, 1))

        self.selected_item_index = 0
        
        self.items = {}

        x = 340 * (self.game.game_resolution.x / game.RES[0])
        y = 45
        dy = 35
        self.items['continue'] = text.Text("CONTINUE", "small", V2(x, y), multiline_width=200, onhover=lambda v:self.onhover(0,v), onclick=self.click_continue)
        if self.game.save.run_state:
            jumps = len(self.game.save.run_state['path'])-1
            if jumps == 1:
                self.items['continue'].set_text("CONTINUE (%d jump)" % jumps)
            else:
                self.items['continue'].set_text("CONTINUE (%d jumps)" % jumps)
        else:
            self.items['continue'].visible = False
            self.items['continue'].selectable = False
        self.items['new'] = text.Text("NEW GAME", "small", V2(x, y + dy * 1), onhover=lambda v:self.onhover(1,v), onclick=self.click_new)
        self.items['tutorial'] = text.Text("TUTORIAL", "small", V2(x, y + dy * 2), onhover=lambda v:self.onhover(2,v), onclick=self.click_tutorial)
        self.items['controls'] = text.Text("CONTROLS", "small", V2(x, y + dy * 3), onhover=lambda v:self.onhover(3,v), onclick=self.click_controls)
        self.items['music'] = text.Text("MUSIC", "small", V2(x, y + dy * 4))
        self.items['sound'] = text.Text("SOUND", "small", V2(x, y + dy * 5))
        self.items['resolution'] = text.Text("RESOLUTION", "small", V2(x, y + dy * 6), onhover=lambda v:self.onhover(6,v), onclick=self.click_resolution)
        self.items['credits'] = text.Text("CREDITS", "small", V2(x, y + dy * 7), onhover=lambda v:self.onhover(7,v))
        self.items['exit'] = text.Text("EXIT", "small", V2(x, y + dy * 8), onhover=lambda v:self.onhover(8,v), onclick=sys.exit)
        
        self.item_names = list(self.items.keys())

        for item in self.items.values():
            self.ui_group.add(item)
        self.update_selection()

        self.music_meter = Slider(V2(x + 50, y + dy * 4), 100, 0, 10, onchange=self.music_change)
        self.ui_group.add(self.music_meter)
        self.sound_meter = Slider(V2(x + 50,  y + dy * 5), 100, 0, 10, onchange=self.sound_change)
        self.ui_group.add(self.sound_meter)        
        self.resolution_display = text.Text("1x1", "small", (x + 80,  y + dy * 6))
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
        self.time += min(dt,0.1)
        self.bg.update(dt)
        for para in self.parallax:
            para.update(self.time)

        for i in range(10):
            s = random.choice(self.stars)
            s.frame = int(s.frame / 2) * 2 + random.randint(0,1)
        super().update(dt)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)
        # for i in range(16, self.game.game_resolution.x, 32):
        #     pygame.draw.line(self.game.screen, PICO_DARKBLUE, (i, 0), (i, self.game.game_resolution.y))
        # for i in range(16, self.game.game_resolution.y, 32):
        #     pygame.draw.line(self.game.screen, PICO_DARKBLUE, (0, i), (self.game.game_resolution.x, i))            
        dirty = []
        dirty.extend(self.background_group.draw(self.game.screen))
        self.game.screen.blit(self.bg.wobble_image, self.bg.pos.tuple_int())
        dirty.extend(self.game_group.draw(self.game.screen))
        dirty.extend(self.ui_group.draw(self.game.screen))
        dirty.extend(super().render())
        return []

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
