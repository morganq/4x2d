import game
import pygame
import text
import scene
import menuscene
from colors import *

class IntroScene(scene.Scene):
    def start(self):
        self.timer = 0
        self.lines = []
        self.group = pygame.sprite.Group()
        self.add_row("A game by Morgan")
        self.add_row("morganquirk@gmail.com")
        self.add_row("Press Space to start")


    def add_row(self, line):
        x = 120 - text.FONTS['small'].get_rect(line)[2] / 2
        t = text.Text(line, "small", (x, len(self.lines) * 15 + 70))
        self.group.add(t)
        self.lines.append(t)

    def take_input(self, inp, event):
        if inp == "action":
            self.game.scene = menuscene.MenuScene(self.game)
            self.game.scene.start()

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.group.draw(self.game.screen)

    def update(self, dt):
        self.timer += dt
        t = self.timer / 2
        for i,te in enumerate(self.lines):
            z = min(max(t - i, 0), 1)
            te.color = [PICO_WHITE[c] * z + PICO_BLACK[c] * (1-z) for c in range(3)]
            te.update()