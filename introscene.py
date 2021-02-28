import game
import pygame
import text
import scene
from v2 import V2
from levelscene import LevelScene
from colors import *

class IntroScene(scene.Scene):
    def start(self):
        self.timer = 0
        self.lines = []
        self.group = pygame.sprite.Group()
        self.add_row("Hostile Quadrant")
        self.add_row("Prototype")
        self.add_row("Send any feedback to morganquirk@gmail.com")
        self.add_row("Press Space to start")
        self.add_row("Thanks for giving it a try!")

    def add_row(self, line):
        x = game.RES[0] / 2 - text.FONTS['small'].get_rect(line)[2] / 2
        t = text.Text(line, "small", V2(x, len(self.lines) * 15 + 70), PICO_WHITE, False, 500)
        print(t.pos)
        self.group.add(t)
        self.lines.append(t)

    def take_input(self, inp, event):
        if inp == "action":
            self.game.scene = LevelScene(self.game)
            self.game.scene.start()

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.group.draw(self.game.screen)

    def update(self, dt):
        self.timer += dt
        t = self.timer
        for i,te in enumerate(self.lines):
            z = min(max(t - i, 0), 1)
            te.color = [PICO_WHITE[c] * z + PICO_BLACK[c] * (1-z) for c in range(3)]
            te.update_image()