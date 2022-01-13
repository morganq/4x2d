import pygame
import states
from stagename import StageName

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
