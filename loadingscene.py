import pygame

import game
import levelscene
from aliens import alien
from button import Button
from colors import *
from framesprite import FrameSprite
from resources import resource_path
from scene import Scene
from simplesprite import SimpleSprite
from states import Machine, UIEnabledState
from text import Text


class LoadingScene(Scene):
    def __init__(self, game, galaxy):
        super().__init__(game)
        self.galaxy = galaxy
        self.rendered = False
        self.loaded = False
        self.levelscene = None
        self.loading_text = None

    def start(self):
        self.group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        alien_obj = alien.ALIENS[self.game.run_info.get_path_galaxy()['alien']]
        nametext = Text(alien_obj.title, "huge", (30, 35), multiline_width=300, center=False)
        self.group.add(nametext)
        self.group.add(Text("SECTOR WARNING", "big", (30, 15), PICO_LIGHTGRAY, multiline_width=300, center=False))
        self.loading_text = Text("Loading...", "small", (game.RES[0] - 70, 325), center=False)
        self.loading_text.offset = (0.5, 0)
        self.group.add(self.loading_text)

        self.group.add(SimpleSprite((0, 65), "assets/aliengraphic.png"))

        tw = 120
        for i,tip in enumerate(alien_obj.tips):
            wp = tw + 20
            x = wp * i + game.RES[0] / 2 - wp
            img = pygame.image.load(resource_path(tip[0]))
            s = SimpleSprite((x, 165), img)
            s.offset = (0.5, 0)
            self.group.add(s)
            if self.game.run_info.get_path_galaxy()['difficulty'] > 1:
                self.group.add(Text(tip[1], "small", (x - 60, 240), multiline_width=120, center=False))
            else:
                # blah
                self.group.add(Text(tip[1], "small", (x - 60, 240), multiline_width=120, center=False))

        self.sm = Machine(UIEnabledState(self))

    def update(self, dt):
        if not self.loaded and self.rendered:
            self.levelscene = levelscene.LevelScene(self.game, self.galaxy.level, self.galaxy.alien, self.galaxy.difficulty)
            self.levelscene.start()
            self.loaded = True
            t = "Start"
            if self.game.input_mode == "joystick":
                t = "[*x*] Start"
            b = Button((game.RES[0] - 80, 320), t, "big", self.on_click_start)
            b.x -= b.width / 2
            self.ui_group.add(b)
            self.loading_text.kill()
        return super().update(dt)

    def on_click_start(self):
        self.game.scene = self.levelscene

    def take_input(self, inp, event):
        if inp == "confirm":
            self.on_click_start()
        return super().take_input(inp, event)

    def render(self):
        self.game.screen.fill(PICO_DARKGRAY)
        self.group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        self.rendered = True 
