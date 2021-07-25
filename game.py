import csv
import io
import sys

import pygame
import xbrz

import allupgradesscene
import buildingcreatorscene
import creditsscene
import introscene
import leveleditorscene
import levelscene
import menuscene
import optimize
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
RES = (500,360)
OBJ = {
}
class Game:
    inst = None
    def __init__(self, save):
        #pygame.display.set_icon(pygame.image.load(resource_path("assets/icon_2_256.png")))
        pygame.mixer.pre_init(buffer=256)
        pygame.init()
        self.save = save
        self.scaled_screen = pygame.display.set_mode((RES[0] * SCALE, RES[1] * SCALE))
        pygame.display.set_caption("Hostile Quadrant")
        sound.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        self.last_joy_axes = None
        #sound.play_music("game")
        self.screen = pygame.Surface(RES, pygame.SRCALPHA)
        self.run_info = run.RunInfo()
        self.input_mode = 'mouse'
        if len(sys.argv) > 1:
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
                
                #if event.type == pygame.KEYUP:
                #    if event.key == pygame.K_SPACE:
                #        self.game_speed_input = 0

                if event.type == pygame.MOUSEBUTTONDOWN:
                    event.gpos = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    if event.button == 1: self.scene.take_input("click", event)
                    if event.button == 3: self.scene.take_input("rightclick", event)

                if event.type == pygame.MOUSEBUTTONUP:
                    event.gpos = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    if event.button == 1: self.scene.take_input("unclick", event)
                    if event.button == 3: self.scene.take_input("unrightclick", event)                    

                if event.type == pygame.MOUSEMOTION:
                    event.gpos = V2(event.pos[0] / SCALE, event.pos[1] / SCALE)
                    event.grel = V2(event.rel[0] / SCALE, event.rel[1] / SCALE)
                    if event.buttons[0]:
                        self.scene.take_input("mouse_drag", event)
                    else:
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
                    #if delta.tuple() != self.last_joy_axes:
                    self.scene.take_input("joymotion", {'delta': delta })
                        #self.last_joy_axes = delta.tuple()

                if event.type == pygame.JOYBUTTONDOWN:
                    try:
                        self.scene.take_input(bindings[event.button], event)
                    except KeyError:
                        self.scene.take_input(None, event)
                    
                #if event.type == pygame.JOYBUTTONUP:
                #    self.scene.take_input("joyup", event)
                #    print(event)

            dt = clock.tick() / 1000.0

            self.scene.update(dt)
            self.render()
            #optimize.print_memos()
            optimize.reset_frame_memos()


    def scale_xbr(self):
        sc = pygame.Surface(self.screen.get_size(), depth=32)
        factor = SCALE
        buf2 = xbrz.scale(bytearray(pygame.image.tostring(self.screen,"RGBA")), factor, RES[0], RES[1], xbrz.ColorFormat.RGB)
        surf = pygame.image.frombuffer(buf2, (RES[0] * factor, RES[1] * factor), "RGBX")
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
        t = pygame.time.get_ticks() - self.frame_time
        self.frame_time = pygame.time.get_ticks()
        text.FONTS['small'].render_to(self.scaled_screen, (5,self.scaled_screen.get_size()[1]-15), "%d ms" % t, (255,255,255,255))
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
