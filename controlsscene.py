import pygame

import game
import menuscene
import text
from colors import PICO_BLACK
from scene import Scene


class ControlsScene(Scene):
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.control_prompts = [
            ('Press [*x*] (Confirm button)','confirm'),
            ('Press [*circle*] (Back button)','back'),
            ('Press [*square*] (Order Ships button)','action'),
            ('Press [*triangle*] (Upgrade button)','special'),
            ('Press the button you want to use for Fast Forward','game_speed'),
            ('Press the button you want to use for Pause','menu'),
        ]
        self.control_index = -1
        self.control_text = text.Text("", "medium", (game.RES[0]/2, game.RES[1]/2), multiline_width=300)
        self.control_text.offset = (0.5, 0.5)
        self.ui_group.add(self.control_text)
        self.bindings = {
            1:"confirm",
            2:"back",
            0:"action",
            3:"special",
            4:"game_speed",
            9:"menu",
            8:"cheat1"
        }
        self.set_next_control_prompt()

    def set_next_control_prompt(self):
        self.control_index += 1
        if self.control_index >= len(self.control_prompts):
            self.game.save.set_setting("controls", self.bindings)
            self.game.save.save()
            self.game.set_scene("options")
        else:
            self.control_text.set_text(self.control_prompts[self.control_index][0])

    def take_input(self, inp, event):
        try:
            if event.type == pygame.JOYBUTTONDOWN:
                print(event.button)
                self.bindings[int(event.button)] = self.control_prompts[self.control_index][1]
                self.set_next_control_prompt()
            else:
                if inp == "back":
                    self.game.set_scene("options")
        except:
            pass
            

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()
