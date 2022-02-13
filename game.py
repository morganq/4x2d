import cProfile
import csv
import io
import os
import pstats
import random
import sys
import threading
import time
import traceback
from collections import defaultdict

import pygame
from pygame.transform import scale

import achievements
import allupgradesscene
import buildingcreatorscene
import creditsscene
import debug
import gameprofile
import introscene
import leveleditorscene
import levelscene
import menuscene
import multiplayermenu
import multiplayerscene
import newgamescene
import optimize
import optionsscene
import planetgenscene
import playerinput
import run
import simplesprite
import sound
import states
import text
import tilemap
import tutorial.tutorial1scene
from colors import *
from helper import clamp, tuple_int
from intel.inteldata import IntelManager, IntelPopup
from resources import resource_path
from starmap import starmapscene

V2 = pygame.math.Vector2

xbrz_scale = False
try:
    import xbrz
    xbrz_scale = True
except:
    pass

DEV = len(sys.argv) > 1 and sys.argv[1] == "dev"
RES = (600,360)
OBJ = {
}
class Game:
    inst = None
    INPUT_MOUSE = "mouse"
    INPUT_JOYSTICK = "joystick"
    INPUT_MULTIPLAYER = "multiplayer"
    def __init__(self, save):
        Game.inst = self
        self.debug_console = False
        global DEV
        #pygame.display.set_icon(pygame.image.load(resource_path("assets/icon_2_256.png")))
        pygame.mixer.pre_init(buffer=256)
        pygame.init()
        self.save = save
        self.achievements = achievements.Achievements(self.save)
        self.intel = IntelManager(self.save)

        resolution = self.save.get_setting("resolution")
        if resolution == None:
            resolution = (1200,800)
            self.save.set_setting("resolution", resolution)
            self.save.save()
        self.set_resolution(V2(*resolution), self.save.get_setting("fullscreen"))
        pygame.display.set_caption("Hostile Quadrant")
        sound.init()
        text.preload()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        self.last_joy_axes = None
        try:
            self.run_info = self.save.get_run_state()
            if not DEV and self.run_info.anticheat_level_started:
                self.run_info.no_score = True
                self.save.set_run_state(self.run_info)
                self.save.save()
        except Exception as e:
            print(e)
            self.run_info = run.RunInfo()
        
        self.input_mode = self.INPUT_MOUSE
        self.player_inputs = []

        self.threads = {}
        self.thread_return_values = {}
        self.thread_index = 0

        if len(sys.argv) > 1:
            DEV = True            
            if sys.argv[1] == "draw":
                self.scene = buildingcreatorscene.BuildingCreatorScene(self)
            elif sys.argv[1] == "editor":
                self.scene = leveleditorscene.LevelEditorScene(self)
            elif sys.argv[1] == "star":
                self.run_info = run.RunInfo()
                self.scene = starmapscene.StarMapScene(self)
            elif sys.argv[1] == "upgrades":
                self.scene = allupgradesscene.AllUpgradesScene(self)
            elif sys.argv[1] == "tutorial":
                self.scene = tutorial.tutorial1scene.Tutorial1Scene(self)
            elif sys.argv[1] == "game":
                self.scene = levelscene.LevelScene(self, "cross", "alien2", 6, 6, "Testing", "This is a test string for the description")
            elif sys.argv[1] == "boss":
                self.scene = levelscene.LevelScene(self, "boss2", "boss", 9, 9, "Boss", "It's the boss")
            elif sys.argv[1] == "planet":
                self.scene = planetgenscene.PlanetGenScene(self)
            elif sys.argv[1] == "new":
                self.scene = newgamescene.NewGameScene(self)
            elif sys.argv[1] == "perf":
                self.scene = levelscene.LevelScene(self, "choke", "alien3", 3, 3, "", "", options='performance')
            elif sys.argv[1] == "flowfield":
                self.scene = levelscene.LevelScene(self, "cross", "alien3", 1, 1, "", "", options='flowfield')
            elif sys.argv[1] == "multiplayer":
                # self.player_inputs = [
                #     playerinput.Player(0, playerinput.Player.INPUT_MOUSE),
                #     playerinput.Player(1, playerinput.Player.INPUT_JOYSTICK, 0),
                #     playerinput.Player(2, playerinput.Player.INPUT_JOYSTICK, 1),
                #     playerinput.Player(3, playerinput.Player.INPUT_JOYSTICK, 2)
                # ]
                # self.input_mode = self.INPUT_MULTIPLAYER
                # self.scene = multiplayerscene.MultiplayerScene(self, 4)
                self.scene = multiplayermenu.MultiplayerMenu(self)
            else:
                self.scene = menuscene.MenuScene(self)
        else:
            self.scene = menuscene.MenuScene(self)
            #self.scene = introscene.IntroScene(self)
        self.playing_level_index = None

        self.game_speed_input = 0
        self.last_joystick_pos = defaultdict(lambda:self.game_resolution / 2)

        self.menu_bg_cache_obj = None

        self.first_load = True
        self.frame_time = 0
        self.frame_times = []
        self.scale_mode = "xbr"
        self.fps_limited_pause = False
        self._profiling = False
        self._profile_start_time = 0
        self._profiler = None

    def set_resolution(self, resolution, fullscreen = False, resizable = False):
        flags = 0
        if fullscreen:
            flags = flags | pygame.FULLSCREEN | pygame.HWSURFACE
        if resizable:
            flags = flags | pygame.RESIZABLE
        self.full_resolution  = V2(resolution)
        self.scale = int(min(self.full_resolution.x / RES[0], self.full_resolution.y / RES[1]))
        self.scaled_screen = pygame.display.set_mode(tuple_int(self.full_resolution), flags=flags)
        self.game_resolution = V2(self.full_resolution // self.scale)
        self.screen = pygame.Surface(tuple_int(self.game_resolution), pygame.SRCALPHA)
        self.game_offset = V2((self.game_resolution.x - RES[0]) / 2,(self.game_resolution.y - RES[1]) / 2)

    def make_resizable(self, resizable):
        self.set_resolution(
            V2(*self.save.get_setting("resolution")),
            self.save.get_setting("fullscreen"),
            resizable
        )

    def process_input_singleplayer(self, event):
        bindings = {int(k):v for k,v in self.save.get_setting("controls").items()}
        reverse_bindings = {v:k for k,v in bindings.items()}
        axes = [0,1]

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT: self.scene.take_input("left", event)
            elif event.key == pygame.K_RIGHT: self.scene.take_input("right", event)
            elif event.key == pygame.K_UP: self.scene.take_input("up", event)
            elif event.key == pygame.K_DOWN: self.scene.take_input("down", event)
            elif event.key == pygame.K_a and DEV:
                ra = random.choice(list(achievements.ACHIEVEMENT_INFO.values()))
                self.show_achievement(ra['name'], ra['description'])
            elif event.key == pygame.K_r and DEV:
                self.achievements.reset_all()             
            elif event.key == pygame.K_BACKQUOTE and DEV:
                self.debug_console = not self.debug_console
            elif event.key == pygame.K_SPACE:
                self.scene.take_input("action", event)
                self.game_speed_input = clamp(int(1 - self.game_speed_input), 0, 1)
            elif event.key == pygame.K_ESCAPE:
                self.scene.take_input("menu", event)
            elif DEV and event.key == pygame.K_p:
                self._profiling = not self._profiling
                if self._profiling:
                    self._profiler = cProfile.Profile()
                    self._profiler.enable()
                    self._profile_start_time=time.time()
                else:
                    self._profiler.disable()
                    stats = pstats.Stats(self._profiler).sort_stats("cumulative")
                    gameprofile.dump_stats(self._profiler, time.time() - self._profile_start_time)
                    
            else:
                self.scene.take_input("other", event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
            if event.button == 1: self.scene.take_input("click", event)
            if event.button == 3:
                self.scene.take_input("rightclick", event)

        elif event.type == pygame.MOUSEBUTTONUP:
            event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
            if event.button == 1: self.scene.take_input("unclick", event)
            if event.button == 3: self.scene.take_input("unrightclick", event)                    

        elif event.type == pygame.MOUSEMOTION:
            event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
            event.__dict__['grel'] = V2(event.rel[0] / self.scale, event.rel[1] / self.scale)
            if event.buttons[0]:
                self.scene.take_input("mouse_drag", event)
            else:
                pass
                self.scene.take_input("mouse_move", event)

        elif event.type == pygame.JOYAXISMOTION:
            delta = V2(self.joysticks[0].get_axis(axes[0]), self.joysticks[0].get_axis(axes[1]))
            if delta.length_squared() < 0.35 ** 2:
                delta = V2(0,0)
            if delta != self.last_joy_axes:
                self.scene.take_input("joymotion", {'delta':delta})
                self.last_joy_axes = delta

        elif event.type == pygame.JOYHATMOTION:
            delta = V2(event.value[0], -event.value[1])
            self.scene.take_input("joymotion", {'delta': delta })

        elif event.type == pygame.JOYBUTTONDOWN:
            try:
                self.scene.take_input(bindings[event.button], event)
            except KeyError:
                self.scene.take_input(None, event)

        if self.input_mode == "joystick":
            self.game_speed_input = [0,1][self.joysticks[0].get_button(reverse_bindings['game_speed'])]                

    def process_input_multiplayer(self, event):
        def get_mouse_player():
            for inp in self.player_inputs:
                if inp.input_type == playerinput.Player.INPUT_MOUSE:
                    return inp
            return None

        def get_joystick_player(joystick_id):
            for inp in self.player_inputs:
                if inp.input_type == playerinput.Player.INPUT_JOYSTICK and inp.joystick_id == joystick_id:
                    return inp
            return None

        p = None
        if event.type == pygame.KEYDOWN:
            p = get_mouse_player()
            if p:
                if event.key == pygame.K_ESCAPE:
                    self.scene.take_player_input(p.player_id, "menu", event)
                elif event.key in [pygame.K_SPACE, pygame.K_u]:
                    self.scene.take_player_input(p.player_id, "game_speed", event)
                else:
                    self.scene.take_player_input(p.player_id, "other", event) # Usually for debug purposes

        elif event.type == pygame.KEYUP:
            p = get_mouse_player()
            if p:
                if event.key in [pygame.K_SPACE, pygame.K_u]:
                    self.scene.take_player_input(p.player_id, "un_game_speed", event)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            p = get_mouse_player()
            if p:
                event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
                if event.button == 1: self.scene.take_player_input(p.player_id, "click", event)
                if event.button == 3: self.scene.take_player_input(p.player_id, "rightclick", event)

        elif event.type == pygame.MOUSEBUTTONUP:
            p = get_mouse_player()
            if p:
                event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
                if event.button == 1: self.scene.take_player_input(p.player_id, "unclick", event)
                if event.button == 3: self.scene.take_player_input(p.player_id, "unrightclick", event)                    

        elif event.type == pygame.MOUSEMOTION:
            p = get_mouse_player()
            if p:            
                event.__dict__['gpos'] = V2(event.pos[0] / self.scale, event.pos[1] / self.scale)
                event.__dict__['grel'] = V2(event.rel[0] / self.scale, event.rel[1] / self.scale)
                if event.buttons[0]:
                    self.scene.take_player_input(p.player_id, "mouse_drag", event)
                else:
                    self.scene.take_player_input(p.player_id, "mouse_move", event)

        elif event.type == pygame.JOYAXISMOTION:
            p = get_joystick_player(event.instance_id)
            
            if p:
                delta = V2(self.joysticks[p.joystick_id].get_axis(p.get_horizontal_axis()), self.joysticks[p.joystick_id].get_axis(p.get_vertical_axis()))
                if delta.length_squared() < 0.35 ** 2:
                    delta = V2(0,0)
                if delta != self.last_joy_axes:
                    self.scene.take_player_input(p.player_id, "joymotion", {'delta':delta})
                    self.last_joy_axes = delta

                #if self.input_mode == "joystick":
                #    self.game_speed_input = [0,1][self.joysticks[0].get_button(reverse_bindings['game_speed'])]

        elif event.type == pygame.JOYHATMOTION:
            p = get_joystick_player(event.instance_id)
            if p:            
                delta = V2(event.value[0], -event.value[1])
                self.scene.take_player_input(p.player_id, "joymotion", {'delta': delta })

        elif event.type == pygame.JOYBUTTONDOWN:
            p = get_joystick_player(event.instance_id)
            if p:          
                try:
                    self.scene.take_player_input(p.player_id, p.get_binding(event.button), event)
                except KeyError:
                    self.scene.take_player_input(p.player_id, None, event)       

        elif event.type == pygame.JOYBUTTONUP:
            p = get_joystick_player(event.instance_id)
            if p:      
                self.scene.take_player_input(p.player_id, "un_game_speed", event)       

        self.scene.take_raw_input(event)

    def run(self):
        self.clock = pygame.time.Clock()
        self.running = True
        self.achievements_group = pygame.sprite.LayeredDirty()
        achievements.init_steam()
        self.scene.start()

        while self.running:
            try:
                self.game_loop()
            except:
                traceback.print_exc()
                val = traceback.format_exc()
                # Set anticheat False so we don't penalize players who hit crash bugs!!
                self.run_info.anticheat_level_started = False
                self.save.set_run_state(self.run_info)
                self.save.save()
                while self.running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            self.running = False

                    self.scaled_screen.fill((0,0,0))
                    text.render_multiline_to(self.scaled_screen, (10,10), "OH NO I CRASHED! Sorry! Please send a screenshot to morganquirk@gmail.com", "big", PICO_RED, wrap_width=500)
                    text.render_multiline_to(self.scaled_screen, (10,70), str(val), "small", PICO_WHITE, wrap_width=500)
                    
                    pygame.display.update()

    def game_loop(self):
        for event in pygame.event.get():
            if event.type == sound.MUSIC_ENDEVENT:
                sound.end_of_music()

            elif event.type == pygame.VIDEORESIZE:
                self.scene.on_display_resize(V2(event.w, event.h))

            elif event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.JOYDEVICEADDED:                    
                self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

            elif self.input_mode in [self.INPUT_MOUSE, self.INPUT_JOYSTICK]:
                self.process_input_singleplayer(event)

            elif self.input_mode == self.INPUT_MULTIPLAYER:
                self.process_input_multiplayer(event)

        # This code sucks but it works. Go through all the threads
        # see if they're done and call their callbacks.
        for thread_index, (thread, callback) in self.threads.items():
            if not thread.is_alive():
                callback(self.thread_return_values[thread_index])
        self.threads = {k:v for k,v in self.threads.items() if v[0].is_alive()}

        max_framerate = 60
        if self.fps_limited_pause:
            pygame.time.wait(20)
        dt = self.clock.tick(max_framerate) / 1000.0
        # limit delta
        dt = min(dt, 0.1)

        s1 = self.scene
        self.scene.update(dt)
        s2 = self.scene
        if s1 == s2: # Skip render if we changed scenes in the middle of an update. Things could go wrong. 
            self.render()
        #optimize.print_memos()
        optimize.reset_frame_memos()

        self.update_achievements(dt)

        return True

    def update_achievements(self, dt):
        y = 0
        for sprite in self.achievements_group.sprites():
            sprite.update(dt)
            if sprite.alive():
                sprite.y = y
                y += sprite.height + 6

    def show_achievement(self, name, description):
        popup = achievements.AchievementPopup(V2(self.game_resolution.x // 2, 0), name, description)
        self.achievements_group.add(popup)

    def show_intel(self, name):
        popup = IntelPopup(V2(self.game_resolution.x // 2, 0), name)
        self.achievements_group.add(popup)

    def scale_xbr(self):
        sc = pygame.Surface(self.screen.get_size(), depth=32)
        factor = self.scale
        grx, gry = int(self.game_resolution.x), int(self.game_resolution.y)
        buf2 = xbrz.scale(bytearray(pygame.image.tostring(self.screen,"RGBA")), factor, grx, gry, xbrz.ColorFormat.RGB)
        surf = pygame.image.frombuffer(buf2, (grx * factor, gry * factor), "RGBX")
        self.scaled_screen.blit(surf, (0,0))

    def scale_normal(self):
        pygame.transform.scale(self.screen, self.scaled_screen.get_size(), self.scaled_screen)

    def draw_debug_console(self):
        y = 0
        for line in debug.DEBUG_LOG[-20:]:
            surf = text.render_multiline(line, "small", PICO_GREEN, 500, False)
            pygame.draw.rect(self.scaled_screen, PICO_BLACK, (0, y, self.scaled_screen.get_width(), surf.get_height() + 2), 0)
            self.scaled_screen.blit(surf, (2, y + 1))
            y += surf.get_height() + 2

    def render(self):
        #self.scaled_screen.fill((128,128,128,255))
        self.scene.render()
        self.achievements_group.draw(self.screen)
        if self.scale == 1 or not xbrz_scale:
            self.scale_normal()
        else:
            if self.scale_mode == "normal":
                self.scale_normal()
            else:
                self.scale_xbr()
        
        if self.debug_console:
            self.draw_debug_console()

        t = pygame.time.get_ticks() - self.frame_time
        self.frame_time = pygame.time.get_ticks()
        self.frame_times.append(t)
        self.frame_times = self.frame_times[-80:]
        avg = 0
        if len(self.frame_times) >= 10:
            remove_spikes = [f for f in self.frame_times if f < 1000]
            avg = sum(remove_spikes) / max(len(remove_spikes),1)
            if not self.fps_limited_pause:
                if avg > 33:
                    pass
                    #self.scale_mode = "normal"
                if avg < 25:
                    self.scale_mode = "xbr"
        if DEV:
            fps_color = (0,255,0,255)
            if avg > 33:
                fps_color = (255,0,0,255)
            elif avg > 25:
                fps_color = (255,255,0,255)
            text.FONTS['small'].render_to(self.scaled_screen, (5,self.scaled_screen.get_size()[1]-15), "%d ms" % avg, fps_color)
            text.FONTS['small'].render_to(self.scaled_screen, (35,self.scaled_screen.get_size()[1]-15), self.input_mode, (255,255,255,255))
        pygame.display.update()

    def get_available_resolutions(self):
        reses = sorted(list(set(pygame.display.list_modes())), reverse=True)
        return reses

    def start_level(self, level, index):
        self.playing_level_index = index
        self.scene = levelscene.LevelScene(self, level)
        self.scene.start()

    def go_to_menu(self):
        self.scene = menuscene.MenuScene(self)
        self.scene.start()

    def set_scene(self, scene_name, *args):
        self.scene = {
            'menu':menuscene.MenuScene,
            'options':optionsscene.OptionsScene,
            'multiplayer_menu':multiplayermenu.MultiplayerMenu,
            "multiplayer":multiplayerscene.MultiplayerScene,
            "starmap":starmapscene.StarMapScene,
            "tutorial":tutorial.tutorial1scene.Tutorial1Scene,
        }[scene_name](self, *args)
        self.scene.start()

    def end_run(self):
        self.save.set_run_state(None)
        self.save.save()
        self.run_info = run.RunInfo()

    def is_xbox(self):
        if self.joysticks:
            return self.joysticks[0].get_numbuttons() != 14
        return False

    def load_in_thread(self, func, callback):
        t = self.thread_index
        def wrapped_func():
            self.thread_return_values[t] = func()
            print("set thread return values for", t, self.thread_return_values[t])
        thread = threading.Thread(target=wrapped_func, daemon=True)
        thread.start()
        self.threads[t] = (thread, callback)
        self.thread_index += 1
