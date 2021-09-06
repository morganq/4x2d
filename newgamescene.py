import pygame

import button
import menuscene
import newgamebackground
import run
import scene
import states
from colors import *
from starmap import starmapscene
from tutorial import tutorialmessage
from v2 import V2


class NewGameScene(scene.Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.bg = newgamebackground.NewGameBackground(V2(0,0))
        self.background_group.add(self.bg)

        self.launch = None
        self.time = 0

        self.back = button.Button(V2(5, 5), "BACK", "big", self.on_back, color=PICO_ORANGE)
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
            self.msg.set_text("Commander! Another distress beacon, out in deep space. Should we go?")
            self.msg.set_visible(True)
            self.msg.pos = V2(self.game.game_resolution.x / 2 - self.msg.width / 2, self.game.game_resolution.y - self.msg.height - 5)
            self.msg.fade_in()
        if self.time > 4 and not self.launch:
            self.launch = button.Button(V2(self.game.game_resolution.x / 2, self.game.game_resolution.y / 2), "LAUNCH", "huge", self.on_launch, color=PICO_ORANGE)
            self.launch.offset = (0.5, 0.5)
            self.ui_group.add(self.launch)            
        self.bg.update(dt)
        for spr in self.ui_group.sprites():
            spr.update(dt)
        return super().update(dt)

    def render(self):   
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)        
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)

    def on_launch(self):
        self.game.run_info = run.RunInfo()
        self.game.scene = starmapscene.StarMapScene(self.game)
        self.game.scene.start()

    def on_back(self):
        self.game.scene = menuscene.MenuScene(self.game)
        self.game.scene.start()