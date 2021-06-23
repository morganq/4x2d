from framesprite import FrameSprite
from simplesprite import SimpleSprite
from states import UIEnabledState, Machine
from scene import Scene
import pygame
from colors import *
from text import Text
from aliens import alien
import game
import levelscene
from button import Button
from resources import resource_path

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
        nametext = Text(alien_obj.title, "huge", (30, 50), multiline_width=300, center=False)
        self.group.add(nametext)
        self.group.add(Text("SECTOR WARNING", "big", (30, 30), PICO_LIGHTGRAY, multiline_width=300, center=False))
        self.loading_text = Text("Loading...", "small", (game.RES[0] / 2, 315), center=False)
        self.loading_text.offset = (0.5, 0)
        self.group.add(self.loading_text)

        self.group.add(SimpleSprite((0, 80), "assets/aliengraphic.png"))

        tw = 120
        for i,tip in enumerate(alien_obj.tips):
            wp = tw + 20
            x = wp * i + game.RES[0] / 2 - wp
            img = pygame.image.load(resource_path(tip[0]))
            s = FrameSprite((x, 200), img, img.get_width() / 2)
            s.offset = (0.5, 0)
            self.group.add(s)
            if self.game.run_info.get_path_galaxy()['difficulty'] > 1:
                self.group.add(Text(tip[1], "small", (x - 60, 220), multiline_width=120, center=False))
            else:
                self.group.add(Text("", "small", (x - 60, 220), multiline_width=120, center=False))

        self.sm = Machine(UIEnabledState(self))

    def update(self, dt):
        if not self.loaded and self.rendered:
            self.levelscene = levelscene.LevelScene(self.game, self.galaxy.level, self.galaxy.alien, self.galaxy.difficulty)
            self.levelscene.start()
            self.loaded = True
            b = Button((game.RES[0] / 2, 310), "Start", "big", self.on_click_start)
            b.x -= b.width / 2
            self.ui_group.add(b)
            self.loading_text.kill()
        return super().update(dt)

    def on_click_start(self):
        self.game.scene = self.levelscene

    def render(self):
        self.game.screen.fill(PICO_DARKGRAY)
        self.group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        self.rendered = True 