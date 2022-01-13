import levelcontroller

from multiplayer.levelstates import MultiplayerVictoryState


class MultiplayerLevelController(levelcontroller.LevelController):
    def update(self, dt):
        if not self.scene.paused:
            self.detect_victory()

    def detect_victory(self):
        winner = None
        tie = False
        winner_mined = 0
        for civ in self.scene.player_civs:
            if civ.total_mined >= self.scene.victory_number:
                if winner:
                    if civ.total_mined > winner_mined:
                        winner = civ
                        winner_mined = civ.total_mined
                        tie = False
                    elif civ.total_mined == winner_mined:
                        tie = True
                    else:
                        pass
                else:
                    winner = civ
                    winner_mined = civ.total_mined

        if winner and not tie:
            self.scene.paused = True
            self.scene.sm.transition(MultiplayerVictoryState(self.scene, winner))

    def detect_defeat(self):
        return
