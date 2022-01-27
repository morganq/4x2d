import pygame

import button
import menuscene
import newgamebackground
import run
import scene
import states
import text
from colors import *
from starmap import starmapscene
from tutorial import tutorialmessage
from tutorial.tutorial1scene import Tutorial1Scene

V2 = pygame.math.Vector2


class NewGameScene(scene.Scene):
    def __init__(self, game, run_challenges = None, run_modifiers = None):
        self.run_challenges = run_challenges or []
        self.run_modifiers = run_modifiers or []
        super().__init__(game)

    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.bg = newgamebackground.NewGameBackground(V2(0,0))
        self.background_group.add(self.bg)

        self.launch = None
        self.loading = False
        self.time = 0

        backtext = "BACK"
        if self.game.input_mode == "joystick": backtext = "[*circle*] BACK"
        self.back = button.Button(V2(5, 5), backtext, "big", self.on_back, color=PICO_ORANGE)
        self.ui_group.add(self.back)

        self.msg = tutorialmessage.TutorialMessage("")
        #self.msg.offset = (0.5, 1)
        self.msg.pos = V2(self.game.game_resolution.x / 2, self.game.game_resolution.y - 5)
        self.msg.add_all_to_group(self.ui_group)
        self.msg._reposition_children()
        self.msg.set_visible(False)
        #self.msg.fade_in()
        

        self.sm = states.Machine(states.UIEnabledState(self))

    def update(self, dt):
        self.time += dt
        if self.time > 0.5 and not self.msg.target_message:
            self.msg.set_text("Commander! A distress signal, coming from deep space. It must be other refugees! Should we go?")
            self.msg.set_visible(True)
            self.msg.pos = V2(self.game.game_resolution.x / 2 - self.msg.width / 2, self.game.game_resolution.y - self.msg.height - 5)
            self.msg.fade_in()
        if self.time > 4.5 and not self.launch:
            if self.game.save.tutorial_complete:
                launch_word = "LAUNCH"
            else:
                launch_word = "LAUNCH" # "tutorial"?
            launchtext = launch_word
            if self.game.input_mode == "joystick": launchtext = "[*x*] %s" % launch_word
            self.launch = button.Button(V2(self.game.game_resolution.x / 2, self.game.game_resolution.y / 2), launchtext, "huge", self.on_launch, color=PICO_ORANGE)
            self.launch.offset = (0.5, 0.5)
            self.ui_group.add(self.launch)
        self.bg.update(dt)
        for spr in self.ui_group.sprites():
            spr.update(dt)
        return super().update(dt)

    def take_input(self, inp, event):
        if inp == "confirm" and self.launch:
            self.launch.onclick()
        if inp == "back" or inp == "menu":
            self.back.onclick()
        return super().take_input(inp, event)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)        
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)

    def on_launch(self):
        self.game.run_info = run.RunInfo()
        self.game.run_info.started = True
        self.game.run_info.run_challenges = self.run_challenges
        self.game.run_info.run_modifiers = self.run_modifiers
        self.game.run_info.begin_run()
        self.game.save.set_run_state(self.game.run_info)
        self.game.save.save()
        if self.game.save.tutorial_complete:
            self.game.scene = starmapscene.StarMapScene(self.game)
            self.game.scene.start()
        else:
            self.loading = True
            self.game.load_in_thread(self.load_tutorial, self.on_tutorial_loaded)
            self.launch.visible = False
            t = text.Text("Loading...", "huge", V2(self.launch.pos))
            t.offset = (0.5, 0.5)
            self.ui_group.add(t)

    def load_tutorial(self):
        tut = Tutorial1Scene(self.game)
        tut.start()
        return tut

    def on_tutorial_loaded(self, tutorial):
        self.game.scene = tutorial

    def on_back(self):
        if self.loading:
            return
        self.game.scene = menuscene.MenuScene(self.game)
        self.game.scene.start()
