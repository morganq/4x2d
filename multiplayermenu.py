import pygame

import game
import menu
import playerinput
import scene
import states
import text
from colors import *
from v2 import V2


class MultiplayerMenu(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.game.input_mode = game.Game.INPUT_MULTIPLAYER
        
        self.player_index = 1

        res = self.game.game_resolution
        self.instructions = text.Text(
            "Click to add a mouse player\nPress a joystick button to add a joystick player.",
            "small",
            V2(res.x/2, 50),
            multiline_width=400
        )
        self.instructions.offset = (0.5, 0)

        self.ui_group.add(self.instructions)

        self.sm = states.Machine(states.UIEnabledState(self))

    def take_raw_input(self, event):
        if event.type == pygame.JOYBUTTONDOWN:
            print("joy", event.instance_id)

            found = False
            for pi in self.game.player_inputs:
                if pi.input_type == playerinput.Player.INPUT_JOYSTICK and pi.joystick_id == event.instance_id:
                    found = True
                    break

            if not found:
                self.game.player_inputs.append(playerinput.Player(self.player_index, playerinput.Player.INPUT_JOYSTICK, event.instance_id))
                self.player_index += 1
                self.ui_group.add(text.Text("Joystick %d" % event.instance_id, "small", V2(self.game.game_resolution.x / 2 - 25, 100 + self.player_index * 20)))


        if event.type == pygame.MOUSEBUTTONDOWN:
            print("mouse")
            found = False
            for pi in self.game.player_inputs:
                if pi.input_type == playerinput.Player.INPUT_MOUSE:
                    found = True
                    break

            if not found:
                self.game.player_inputs.append(playerinput.Player(self.player_index, playerinput.Player.INPUT_MOUSE))
                self.player_index += 1
                self.ui_group.add(text.Text("Mouse", "small", V2(self.game.game_resolution.x / 2 - 25, 100 + self.player_index * 20)))

    def take_player_input(self, p, inp, event):
        print(p, inp, event)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()            