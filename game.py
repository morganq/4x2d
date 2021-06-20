import pygame
import csv

import sound
import tilemap
import states
import levelscene
from starmap import starmapscene
import introscene
import buildingcreatorscene
import leveleditorscene
import allupgradesscene
from resources import resource_path
import sys
import menuscene
import creditsscene
import simplesprite
import text
from colors import *
from v2 import V2
import run
import optimize
import xbrz
import tutorial.tutorial1scene
import io

DEV = True
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
        #sound.play_music("game")
        self.screen = pygame.Surface(RES, pygame.SRCALPHA)
        self.run_info = run.RunInfo()
        self.input_mode = 'mouse'
        if len(sys.argv) > 1 and DEV:
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
                self.scene = levelscene.LevelScene(self, None, None, 1, sys.argv[1])
        else:
            self.scene = menuscene.MenuScene(self)
            #self.scene = introscene.IntroScene(self)
        self.playing_level_index = None

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
                    elif event.key == pygame.K_SPACE: self.scene.take_input("action", event)
                    elif event.key == pygame.K_ESCAPE:
                        self.scene.take_input("back", event)
                    else:
                        self.scene.take_input("other", event)

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
            self.scale_xbr()
        t = pygame.time.get_ticks() - self.frame_time
        self.frame_time = pygame.time.get_ticks()
        text.FONTS['small'].render_to(self.scaled_screen, (5,self.scaled_screen.get_size()[1]-15), "%d ms" % t, (255,255,255,255))
        pygame.display.update()

    def start_level(self, level, index):
        self.playing_level_index = index
        self.scene = levelscene.LevelScene(self, level)
        self.scene.start()

    def return_to_map(self, won=False):
        level = self.playing_level_index
        if won and self.playing_level_index is not None:
            level = self.playing_level_index + 1
        self.scene = worldmapscene.WorldMapScene(self, level)
        self.scene.start() 

    def record_victory(self, steps):
        if self.playing_level_index is not None:
            level = worldmapscene.LEVELS[self.playing_level_index]
            s3, s2, s1 = level[4:]
            print(steps, s3,s2,s1)
            stars = 0
            if steps <= s3: stars = 3
            elif steps <= s2: stars = 2
            elif steps <= s1: stars = 1
            old_state = self.save.get_level_state(self.playing_level_index)
            if not old_state['beaten'] or steps < old_state['steps'] or stars > old_state['stars']:
                self.save.set_level_state(self.playing_level_index, True, steps, stars)
                self.save.save()

    def go_to_menu(self):
        self.scene = menuscene.MenuScene(self)
        self.scene.start()

    def update_scale(self, scale):
        global SCALE
        SCALE = scale
        self.scaled_screen = pygame.display.set_mode((RES[0] * SCALE, RES[1] * SCALE))
