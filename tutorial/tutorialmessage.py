import random

import sound
from framesprite import FrameSprite
from panel import Panel
from simplesprite import SimpleSprite
from text import Text
import pygame
V2 = pygame.math.Vector2


class TutorialMessage(Panel):
    def __init__(self, message):
        super().__init__(V2(0,0), None)
        self.padding = 8

        self.face = FrameSprite(V2(0,0), "assets/tutorialface.png", 28)
        self.add(self.face, V2(0,0))

        self.target_message = ""
        self.text = Text(message, "small", V2(0,0), multiline_width=300, center=False)
        self.add(self.text, V2(34, 3))

        self.talk_timer = len(message) / 20
        self.shown_time = 0
        self.speed = 1
        self.done = True

        self.redraw()

    def set_text(self, text):
        self.text.set_text("")
        self.target_message = text
        self.text._width = 300
        self.redraw()
        self.talk_timer = len(text) / 20
        self.shown_time = 0
        self.speed = 1
        self.done = False

    def update(self, dt):
        dt *= self.speed
        self.talk_timer -= dt
        self.shown_time += dt
        if self.shown_time > 0.5 and len(self.text._text) < len(self.target_message):
            speed = 7.5
            tt = self.talk_timer * speed
            if tt % 1 < 0.5 and (tt + dt * speed) % 1 >= 0.5:
                sound.play(random.choice(['talk1', 'talk2', 'talk3']))
                self.face.frame = random.randint(0,2)

            self.text.set_text(self.target_message[0:int((self.shown_time - 0.5) * 30)])
            self.text._width = 300
            self.redraw()

        else:
            self.face.frame = 2

        if len(self.text._text) >= len(self.target_message):
            self.done = True
        return super().update(dt)
