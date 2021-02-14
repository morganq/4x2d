import game
import pygame
import text
import scene
import menuscene

class CreditsScene(scene.Scene):
    def start(self):
        self.timer = 0
        self.lines = []
        self.group = pygame.sprite.Group()
        self.add_row("Code, Art, Sound, etc.: Morgan Quirk")
        self.add_row("")
        self.add_row("Thanks to:")
        self.add_row("Gizmo199, 7aylor, and GDQ community")
        self.add_row("Pepper, and Socialist Game Devs community")
        self.add_row("Brad A, Matt W, Justin B")
        self.add_row("")
        self.add_row("Shout out:")
        self.add_row("Seattle - CHAZ/CHOP, Socialist Alternative")
        self.add_row("Oakland - Black Lives Matter Movement")
        self.add_row("Chile - End of Pinochet Constitution")
        self.add_row("Barcelona - Independence Referendum")
        self.add_row("Algeria - Movement against Bouteflika")
        self.add_row("Belarus - Movement against Lukashenko")
        self.add_row("Iran - Uprising against Fuel Price Hike")
        self.add_row("India - General Strike")
        self.add_row("Hong Kong - Uprising against Extradition Law")
        self.add_row("New York City - ... To Be Determined")
        self.add_row("")
        self.add_row("Thanks for playing!")


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
        self.game.screen.fill(game.BGCOLOR)
        self.group.draw(self.game.screen)

    def update(self, dt):
        self.timer += dt
        t = self.timer / 2
        for i,te in enumerate(self.lines):
            z = min(max(t - i, 0), 1)
            te.color = [game.FGCOLOR[c] * z + game.BGCOLOR[c] * (1-z) for c in range(3)]
            te.update()
            te.set_pos(te.pos[0], te.pos[1] - dt * 5)

        if self.timer > 45:
            self.game.scene = menuscene.MenuScene(self.game)
            self.game.scene.start()
            
            