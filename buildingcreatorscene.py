from scene import Scene
import pygame
from colors import *
import text
import game
from v2 import V2
import json

GRIDSIZE = 10
CONTROLS = '1234567890QWERTYUIOP'

class BuildingCreatorScene(Scene):
    def __init__(self, game):
        super().__init__(game)

    def start(self):
        self.current_color = PICO_WHITE
        self.shapes = [{'color':PICO_WHITE, 'points':[]}]

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        for x in range(game.RES[0] // GRIDSIZE):
            pygame.draw.line(self.game.screen, PICO_DARKGRAY, (x * GRIDSIZE, 0), (x * GRIDSIZE, game.RES[1]), 1)
        for y in range(game.RES[1] // GRIDSIZE):
            pygame.draw.line(self.game.screen, PICO_DARKGRAY, (0, y * GRIDSIZE), (game.RES[0], y * GRIDSIZE), 1)
        
        pygame.draw.arc(self.game.screen, PICO_PURPLE, (0, game.RES[1] - 100, game.RES[0], 400), -3.14159, 3.14159)

        pygame.draw.line(self.game.screen, PICO_WHITE, (game.RES[0]/2 - GRIDSIZE / 2, game.RES[1] - 90), (game.RES[0]/2 - GRIDSIZE / 2, game.RES[1] - 110), 1)

        for i, color in enumerate(ALL_COLORS):
            pygame.draw.rect(self.game.screen, color, (i * GRIDSIZE, 0, GRIDSIZE, GRIDSIZE))
            text.FONTS['small'].render_to(self.game.screen, (i * GRIDSIZE + 1, 1), CONTROLS[i], PICO_WHITE)

        for shape in self.shapes:
            pts = [(p * GRIDSIZE).tuple_int() for p in shape['points']]
            for pt in pts:
                pygame.draw.circle(self.game.screen, shape['color'], pt, 3, 1)
            if len(pts) > 2:
                pygame.draw.polygon(self.game.screen, shape['color'], pts, 0)

    def take_input(self, inp, event):
        if inp == "click":
            pos = V2(int(event.gpos.x / GRIDSIZE), int(event.gpos.y / GRIDSIZE)) + V2(0.5, 0.5)
            self.shapes[-1]['points'].append(pos)

        if inp == "other":
            controls = {getattr(pygame, "K_%s" % c.lower()):i for i,c in enumerate(CONTROLS)}
            if event.key in controls.keys():
                i = controls[event.key]
                if len(self.shapes[-1]['points']) > 2:
                    self.shapes.append({'color':ALL_COLORS[i], 'points':[]})
                else:
                    self.shapes[-1] = {'color':ALL_COLORS[i], 'points':[]}

            if event.key == pygame.K_BACKSPACE:
                self.shapes.pop()
                if not self.shapes:
                    self.shapes.append({'color':self.current_color, 'points':[]})

            if event.key == pygame.K_z and self.shapes[-1]['points']:
                self.shapes[-1]['points'].pop()

            if event.key == pygame.K_RETURN:
                fname = input("filename> ")
                val = [
                    ([(p + V2(-game.RES[0] / 2 / GRIDSIZE,-100 / GRIDSIZE)).tuple() for p in s['points']], s['color'])
                    for s in self.shapes
                ]
                json.dump(val, open("assets/buildings/%s.json" % fname, "w"))