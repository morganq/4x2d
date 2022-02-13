import pygame
import states
from pausepanel import PausePanel
from stagename import StageName

from multiplayer import inputstates

# States that the multiplayer level can be in - intro, normal, end

class MultiplayerNormalState(states.State):
    pass

class MultiplayerVictoryState(states.State):
    def __init__(self, scene, winner):
        super().__init__(scene)
        self.winner = winner

    def enter(self):
        super().enter()
        sn = StageName(pygame.math.Vector2(0,70), 0, "Victory!", "%s has collected the most resources!" % self.winner.name)
        sn.time = 1.75
        self.scene.ui_group.add(sn)
        self.time = 0

    def paused_update(self, dt):
        self.time += dt
        if self.time > 6.5:
            self.end()
        return super().paused_update(dt)

    def end(self):
        self.scene.game.set_scene("menu")

class MultiplayerInGameMenuState(states.State):
    def __init__(self, scene, invoker):
        super().__init__(scene)
        self.invoker = invoker
        self.old_states = {}

    def enter(self):
        self.panel = PausePanel(pygame.Vector2(0,0), None, self.on_resume, None, self.on_quit)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in()
        self.panel.add_all_to_group(self.scene.ui_group)

        for i,player_sm in self.scene.player_input_sms.items():
            self.old_states[i] = player_sm.state
            if self.scene.get_player_id(self.invoker) == i:
                player_sm.transition(inputstates.MenuState(self.scene, player_sm.state.civ, player_sm.state.input_mode))
            else:
                player_sm.transition(inputstates.NoInputState(self.scene, player_sm.state.civ, player_sm.state.input_mode))

        self.scene.paused = True
        self.scene.game.fps_limited_pause = True

        return super().enter()

    def on_resume(self):
        self.scene.menu_unpause()

    def on_quit(self):
        self.scene.game.set_scene("menu")

    def exit(self):
        self.panel.kill()
        for i, old_state in self.old_states.items():
            self.scene.player_input_sms[i].transition(inputstates.CursorState(self.scene, old_state.civ, old_state.input_mode))
        self.scene.paused = False
        self.scene.game.fps_limited_pause = False
        return super().exit()
