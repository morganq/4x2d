import levelstates


class LevelController:
    def __init__(self, scene):
        self.scene = scene

    def update(self, dt):
        if not self.scene.is_tutorial:
            self.detect_victory()
            if not self.scene.paused:
                self.detect_defeat()

    def detect_victory(self):
        if not self.scene.get_civ_planets(self.scene.enemy.civ):
            self.scene.paused = True
            self.scene.sm.transition(levelstates.VictoryState(self.scene))

    def detect_defeat(self):
        if not self.scene.get_civ_planets(self.scene.my_civ):
            self.scene.paused = True
            self.scene.sm.transition(levelstates.GameOverState(self.scene))        
