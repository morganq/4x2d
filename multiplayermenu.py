import random

import pygame

import button
import game
import menu
import multiplayerscene
import playerinput
import scene
import spritebase
import states
import text
from colors import *
from helper import clamp
from resources import resource_path
from upgrade import upgradeicon, upgrades

V2 = pygame.math.Vector2

PLAYER_COLORS = [
    PICO_BLUE,
    PICO_ORANGE,
    PICO_GREEN,
    PICO_PINK
]
PLAYER_NAMES = [
    'Blue', 'Orange', 'Green', 'Pink'
]

PANEL_POSITIONS = {
    1: [V2(0.33, 0.33)],
    2: [V2(0.33, 0.33), V2(0.66, 0.66)],
    3: [V2(0.33, 0.66), V2(0.5, 0.33), V2(0.66, 0.66)],
    4: [V2(0.33, 0.33), V2(0.66, 0.33), V2(0.33, 0.66), V2(0.66, 0.66)],
}

class MultiplayerUIState(states.UIEnabledState):
    pass
    #def take_input(self, inp, event):
    #    pass


class PlayerInfoPanel(spritebase.SpriteBase):
    def __init__(self, pos, color, number, name, input_type):
        super().__init__(game.Game.inst.game_resolution / 2)
        self._offset = (0.5, 0.5)
        self.target_pos = pos
        self.number = number
        self.color = color
        self.name = name
        self.input_type = input_type
        self.input_image = pygame.image.load(resource_path("assets/%s.png" % self.input_type)).convert_alpha()
        self.upgrade = None
        self.rolling = False
        self.roll_speed = 100
        self.roll_timer = 0
        self._generate_image()

    def _generate_image(self, upgrade=None):
        w,h = 120, 120
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        self.image.fill(self.color)
        pygame.draw.rect(self.image, PICO_WHITE, (2,2,w-4,h-4), 1)
        t1 = text.render_multiline("PLAYER %d" % self.number, "small", PICO_WHITE, wrap_width=120)
        self.image.blit(t1, (10, 10))
        self.image.blit(self.input_image, (w - 32, 22))
        t2 = text.render_multiline("%s" % self.name, "big", PICO_WHITE, wrap_width=120)
        self.image.blit(t2, (10, 26))        

        if self.upgrade:
            surf = upgradeicon.generate_upgrade_image(self.upgrade)
            self.image.blit(surf, (w // 2 - surf.get_width() // 2, 48))
            t3 = text.render_multiline("%s" % self.upgrade.title, "small", PICO_WHITE, wrap_width=100)
            self.image.blit(t3, (w // 2 - t3.get_width() // 2, 84))            
        else:
            pygame.draw.rect(self.image, PICO_LIGHTGRAY, (w // 2 - 10,51,23,23), 1)


        self._width, self._height = w,h
        self._recalc_rect()

    def update(self, dt):
        self.pos = self.pos * 0.9 + self.target_pos * 0.1
        if self.rolling:
            self.roll_timer -= self.roll_speed * dt
            if self.roll_timer < 0:
                self.upgrade = random.choice(
                    [
                        u for u in list(upgrades.UPGRADE_CLASSES.values())
                        if (u.alien == False and u.category in ['buildings','tech'] and 
                        ('2' in u.name or '3' in u.name) and
                        u.resource_type in ['ice', 'gas']
                        )
                    ]
                )
                self._generate_image()
                self.roll_timer = 1
            self.roll_speed = clamp(self.roll_speed - dt * 50, 0, 100)
        return super().update(dt)
    

class MultiplayerMenu(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.game.player_inputs = []
        
        self.player_index = 0

        res = self.game.game_resolution
        self.instructions = text.Text(
            "Click or press START to join the battle!",
            "small",
            V2(res.x/2, 40),
            multiline_width=400,
        )
        self.instructions.offset = (0.5, 0)

        self.ui_group.add(self.instructions)

        self.back = button.Button(V2(10,10), "Back", "big", self.on_back)
        self.ui_group.add(self.back)

        self.start_btn = button.Button(V2(res.x/2,res.y - 40), "[*x*] Ready", "big", None)
        self.start_btn.disabled = True
        self.start_btn.offset = (0.5, 0)
        self.ui_group.add(self.start_btn)

        self.sm = states.Machine(MultiplayerUIState(self))
        self.game.input_mode = game.Game.INPUT_MULTIPLAYER
        self.player_panels = []
        self.mode = "add_players"

    def add_player(self, input_type, joystick_id=None):
        if len(self.game.player_inputs) > 3:
            return
        self.start_btn.disabled = False
        self.start_btn.onclick_callback = self.on_roll
        if input_type == "joystick":
            self.game.player_inputs.append(playerinput.Player(self.player_index, playerinput.Player.INPUT_JOYSTICK, joystick_id=joystick_id))
        else:
            self.game.player_inputs.append(playerinput.Player(self.player_index, playerinput.Player.INPUT_MOUSE))
        
        self.player_index += 1        
        pos = PANEL_POSITIONS[self.player_index][self.player_index - 1]
        
        pip = PlayerInfoPanel(
            V2(pos.x * self.game.game_resolution.x, pos.y * self.game.game_resolution.y),
            PLAYER_COLORS[self.player_index - 1],
            self.player_index,
            PLAYER_NAMES[self.player_index - 1],
            input_type
        )
        self.player_panels.append(pip)
        self.ui_group.add(pip)
        for i,pip in enumerate(self.player_panels):
            pos = PANEL_POSITIONS[self.player_index][i]
            pip.target_pos = V2(pos.x * self.game.game_resolution.x, pos.y * self.game.game_resolution.y)

        print(self.game.player_inputs)

    def take_raw_input(self, event):
        if self.mode != 'add_players':
            return
        if event.type == pygame.JOYBUTTONDOWN:
            found = False
            for pi in self.game.player_inputs:
                if pi.input_type == playerinput.Player.INPUT_JOYSTICK and pi.joystick_id == event.instance_id:
                    found = True
                    break

            if not found:
                pi = playerinput.Player(self.player_index, playerinput.Player.INPUT_JOYSTICK, event.instance_id)
                # If the button pressed was back, screw all this, go back to menu
                if pi.get_binding(event.button) == 'back':
                    self.on_back()
                if pi.get_binding(event.button) == 'menu':
                    self.add_player("joystick", event.instance_id)


        if event.type == pygame.MOUSEBUTTONDOWN:
            event.__dict__['gpos'] = V2(event.pos[0] / self.game.scale, event.pos[1] / self.game.scale)
            self.sm.state.take_input("click", event)            
            # Still want to process the click to check for the back button
            found = False
            for pi in self.game.player_inputs:
                if pi.input_type == playerinput.Player.INPUT_MOUSE:
                    found = True
                    break

            if not found:
                print("add player")
                self.add_player("mouse")

        if event.type == pygame.MOUSEMOTION:
            event.__dict__['gpos'] = V2(event.pos[0] / self.game.scale, event.pos[1] / self.game.scale)
            self.sm.state.take_input("mouse_move", event)

        self.game.input_mode = game.Game.INPUT_MULTIPLAYER

    def take_player_input(self, p, inp, event):
        if inp in ["click", "mousemotion"]:
            self.take_input(inp, event)
        if inp == "confirm":
            if self.mode == "add_players":
                self.on_roll()
            if self.mode == "ready":
                self.on_start()

        self.sm.state.take_input(inp, event)
        self.game.input_mode = game.Game.INPUT_MULTIPLAYER

    def on_roll(self):
        if len(self.player_panels) <= 0:
            return
        for pip in self.player_panels:
            pip.rolling = True
        self.mode = "rolling"
        self.start_btn.text = "Rolling..."
        self.start_btn.color = PICO_LIGHTGRAY
        self.start_btn._generate_image()
        self.start_btn.onclick_callback = None
        self.start_btn.disabled = True

    def on_back(self):
        self.game.set_scene("menu")

    def on_start(self):
        self.game.load_in_thread(self.load_scene, self.done_loading_scene)
        self.start_btn.text = "Loading..."
        self.start_btn.color = PICO_LIGHTGRAY
        self.start_btn._generate_image()
        self.start_btn.disabled = True

    def load_scene(self):
        mps = multiplayerscene.MultiplayerScene(self.game, len(self.player_panels))
        mps.start()
        return mps

    def done_loading_scene(self, scene):
        self.game.scene = scene

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()          

    def update(self, dt):
        for spr in self.ui_group.sprites():
            spr.update(dt)
        if self.mode == "rolling" and self.player_panels[0].roll_speed <= 0:
            self.mode = "ready"
            self.start_btn.text = "[*x*] Start"
            self.start_btn.color = PICO_BLUE
            self.start_btn._generate_image()
            self.start_btn.onclick_callback = self.on_start
            self.start_btn.disabled = False
        self.game.input_mode = game.Game.INPUT_MULTIPLAYER
        return super().update(dt)  
