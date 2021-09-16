import csv
import io
import sys

import pygame
import xbrz
from pygame.transform import scale

import allupgradesscene
import buildingcreatorscene
import creditsscene
import introscene
import leveleditorscene
import levelscene
import menuscene
import newgamescene
import optimize
import planetgenscene
import run
import simplesprite
import sound
import states
import text
import tilemap
import tutorial.tutorial1scene
from colors import *
from helper import clamp
from resources import resource_path
from starmap import starmapscene
from v2 import V2

DEV = len(sys.argv) > 1 and sys.argv[1] == "dev"
SCALE = 2
RES = (600,360)
OBJ = {
}
class Game:
    inst = None
    def __init__(self, save):
        #pygame.display.set_icon(pygame.image.load(resource_path("assets/icon_2_256.png")))
        pygame.mixer.pre_init(buffer=256)
        pygame.init()
        self.save = save
        modes = pygame.display.list_modes()
        print(modes)
        #self.set_resolution(V2(1920, 1080), True)
        self.set_resolution(V2(1220, 800), False)
        pygame.display.set_caption("Hostile Quadrant")
        sound.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        self.last_joy_axes = None
        #sound.play_music("game")
        self.run_info = run.RunInfo()
        self.input_mode = 'mouse'
        if len(sys.argv) > 1:
            global DEV
            DEV = True            
            if sys.argv[1] == "draw":
                self.scene = buildingcreatorscene.BuildingCreatorScene(self)
            elif sys.argv[1] == "editor":
                self.scene = leveleditorscene.LevelEditorScene(self)
            elif sys.argv[1] == "star":
                self.scene = starmapscene.StarMapScene(self)
            elif sys.argv[1] == "upgrades":
                self.scene = allupgradesscene.AllUpgradesScene(self)
            elif sys.argv[1] == "tutorial":
                self.scene = tutorial.tutorial1scene.Tutorial1Scene(self)
            elif sys.argv[1] == "game":
                self.scene = levelscene.LevelScene(self, "choke", "alien3", 3, 3, "Testing", "This is a test string for the description")
            elif sys.argv[1] == "boss":
                self.scene = levelscene.LevelScene(self, "boss", "boss", 9, 9, "Boss", "It's the boss")
            elif sys.argv[1] == "planet":
                self.scene = planetgenscene.PlanetGenScene(self)
            elif sys.argv[1] == "new":
                self.scene = newgamescene.NewGameScene(self)
            elif sys.argv[1] == "perf":
                self.scene = levelscene.LevelScene(self, "choke", "alien3", 3, 3, "", "", options='performance')
            else:
                self.scene = menuscene.MenuScene(self)
        else:
            self.scene = menuscene.MenuScene(self)
            #self.scene = introscene.IntroScene(self)
        self.playing_level_index = None

        self.game_speed_input = 0
        self.last_joystick_pos = V2(200,200)

        self.frame_time = 0
        Game.inst = self

    def set_resolution(self, resolution, fullscreen = False):
        global SCALE
        flags = 0
        if fullscreen:
            flags = flags | pygame.FULLSCREEN | pygame.HWSURFACE | pygame.SCALED
        self.full_resolution = resolution.copy()
        SCALE = int(min(self.full_resolution.x / RES[0], self.full_resolution.y / RES[1]))
        self.scaled_screen = pygame.display.set_mode(self.full_resolution.tuple(), flags=flags)
        self.game_resolution = V2(*(self.full_resolution / SCALE).tuple_int())
        self.screen = pygame.Surface(self.game_resolution.tuple_int(), pygame.SRCALPHA)
        self.game_offset = V2((self.game_resolution.x - RES[0]) / 2,(self.game_resolution.y - RES[1]) / 2)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        self.scene.start()

        while running:
            for event in pygame.event.get():
                if event.type == sound.MUSIC_ENDEVENT:
                    sound.end_of_music()

                if event.type == pygame.QUIT:
                    running = False

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT: self.scene.take_input("left", event)
                    elif event.key == pygame.K_RIGHT: self.scene.take_input("right", event)
                    elif event.key == pygame.K_UP: self.scene.take_input("up", event)
                    elif event.key == pygame.K_DOWN: self.scene.take_input("down", event)
                    elif event.key == pygame.K_SPACE:
                        self.scene.take_input("action", event)
                        self.game_speed_input = clamp(int(1 - self.game_speed_input), 0, 1)
                    elif event.key == pygame.K_ESCAPE:
                        self.scene.take_input("menu", event)
                    else:
                        self.scene.take_input("other", event)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    event.__dict__['gpos'] = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    if event.button == 1: self.scene.take_input("click", event)
                    if event.button == 3: self.scene.take_input("rightclick", event)

                if event.type == pygame.MOUSEBUTTONUP:
                    event.__dict__['gpos'] = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    if event.button == 1: self.scene.take_input("unclick", event)
                    if event.button == 3: self.scene.take_input("unrightclick", event)                    

                if event.type == pygame.MOUSEMOTION:
                    event.__dict__['gpos'] = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    event.__dict__['grel'] = V2(event.rel[0] / SCALE, event.rel[1] / SCALE)
                    if event.buttons[0]:
                        self.scene.take_input("mouse_drag", event)
                    else:
                        pass
                        self.scene.take_input("mouse_move", event)

                bindings = {int(k):v for k,v in self.save.get_setting("controls").items()}
                reverse_bindings = {v:k for k,v in bindings.items()}
                axes = [0,1]

                if event.type == pygame.JOYDEVICEADDED:
                    self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]                    

                if event.type == pygame.JOYAXISMOTION:
                    delta = V2(self.joysticks[0].get_axis(axes[0]), self.joysticks[0].get_axis(axes[1]))
                    if delta.sqr_magnitude() < 0.35 ** 2:
                        delta = V2(0,0)
                    if delta.tuple() != self.last_joy_axes:
                        self.scene.take_input("joymotion", {'delta':delta})
                        self.last_joy_axes = delta.tuple()

                    if self.input_mode == "joystick":
                        self.game_speed_input = [0,1][self.joysticks[0].get_button(reverse_bindings['game_speed'])]

                if event.type == pygame.JOYHATMOTION:
                    delta = V2(event.value[0], -event.value[1])
                    self.scene.take_input("joymotion", {'delta': delta })

                if event.type == pygame.JOYBUTTONDOWN:
                    try:
                        self.scene.take_input(bindings[event.button], event)
                    except KeyError:
                        self.scene.take_input(None, event)
                    
                #if event.type == pygame.JOYBUTTONUP:
                #    self.scene.take_input("joyup", event)
                #    print(event)

            dt = clock.tick() / 1000.0

            s1 = self.scene
            self.scene.update(dt)
            s2 = self.scene
            if s1 == s2: # Skip render if we changed scenes in the middle of an update. Things could go wrong. 
                self.render()
            #optimize.print_memos()
            optimize.reset_frame_memos()


    def scale_xbr(self):
        sc = pygame.Surface(self.screen.get_size(), depth=32)
        factor = SCALE
        buf2 = xbrz.scale(bytearray(pygame.image.tostring(self.screen,"RGBA")), factor, self.game_resolution.x, self.game_resolution.y, xbrz.ColorFormat.RGB)
        surf = pygame.image.frombuffer(buf2, (self.game_resolution.x * factor, self.game_resolution.y * factor), "RGBX")
        self.scaled_screen.blit(surf, (0,0))

    def scale_normal(self):
        pygame.transform.scale(self.screen, self.scaled_screen.get_size(), self.scaled_screen)

    def render(self):
        self.scaled_screen.fill((128,128,128,255))
        self.scene.render()
        if SCALE == 1:
            self.scale_normal()
        else:
            #self.scale_normal()
            self.scale_xbr()
        if True:
            t = pygame.time.get_ticks() - self.frame_time
            self.frame_time = pygame.time.get_ticks()            
            text.FONTS['small'].render_to(self.scaled_screen, (5,self.scaled_screen.get_size()[1]-15), "%d ms" % t, (255,255,255,255))
            #print(t)
        pygame.display.update()

    def start_level(self, level, index):
        self.playing_level_index = index
        self.scene = levelscene.LevelScene(self, level)
        self.scene.start()

    def go_to_menu(self):
        self.scene = menuscene.MenuScene(self)
        self.scene.start()

    def update_scale(self, scale):
        global SCALE
        SCALE = scale
        self.scaled_screen = pygame.display.set_mode((RES[0] * SCALE, RES[1] * SCALE))

    def set_scene(self, scene_name):
        self.scene = {
            'menu':menuscene.MenuScene(self)
        }[scene_name]
        self.scene.start()

    def is_xbox(self):
        if self.joysticks:
            return self.joysticks[0].get_numbuttons() != 14
        return False
