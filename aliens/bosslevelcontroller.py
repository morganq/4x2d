import game
import levelcontroller
import levelstates
from helper import clamp

from aliens import bossmothership

PHASE_1 = 1
PHASE_REVIVING = 2
PHASE_2 = 3

class BossLevelController(levelcontroller.LevelController):
    def __init__(self, scene):
        super().__init__(scene)
        self.phase = PHASE_1
        self.reviving_time = 0
        self.mothership = None

    def update(self, dt):
        super().update(dt)
        if self.phase == PHASE_REVIVING:
            self.reviving_time += dt
            self.scene.game_speed = clamp(self.reviving_time / 3, 1, 20)
            if self.mothership.state == self.mothership.STATE_GAME_WAITING:
                self.phase = PHASE_2
                self.scene.game_speed = 1
                self.scene.sm.transition(levelstates.PlayState(self.scene))

    def detect_victory(self):
        if self.phase == PHASE_1:
            if not self.scene.get_civ_planets(self.scene.enemy.civ):
                self.phase = PHASE_REVIVING
                self.scene.sm.transition(levelstates.CinematicState(self.scene))
                self.mothership = bossmothership.BossMothership(self.scene, game.Game.inst.game_resolution * 0.5)
                self.scene.game_group.add(self.mothership)
                all_planets_by_x = sorted(self.scene.get_planets(), key=lambda p:p.x, reverse=True)
                self.mothership.planets_to_revive = all_planets_by_x[0:len(all_planets_by_x) // 2]
