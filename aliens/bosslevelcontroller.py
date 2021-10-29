import game
import levelcontroller
import levelstates
from helper import clamp
from v2 import V2

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
        self.post_cinematic_timer = 30

    def update(self, dt):
        super().update(dt)
        if self.phase == PHASE_REVIVING:
            self.reviving_time += dt
            #self.scene.game_speed = clamp(self.reviving_time / 4, 1, 20)
            self.scene.game_speed = 20
            if self.mothership.state == self.mothership.STATE_GAME_WAITING:
                self.post_cinematic_timer -= dt
                if self.post_cinematic_timer <= 0:
                    self.phase = PHASE_2
                    self.scene.game_speed = 1
                    self.scene.sm.transition(levelstates.PlayState(self.scene))
                    self.mothership.health_bar.visible = True
                    self.mothership.health_bar.stay = True
                    for p in self.scene.get_planets():
                        p.cinematic_disable = False

            # Make ships go into cinematic mode so they don't fight.
            for ship in self.scene.get_ships():
                ship.cinematic_no_combat = True
            for p in self.scene.get_planets():
                p.cinematic_disable = True                

    def detect_victory(self):
        if self.phase == PHASE_1:
            if not self.scene.get_civ_planets(self.scene.enemy.civ):
                self.scene.game.run_info.o2 += 600 # 10 more minutes
                # TODO: remove this
                #self.scene.paused = True
                #self.scene.sm.transition(levelstates.BeatGameState(self.scene))
                #return
                self.phase = PHASE_REVIVING

                for ship in self.scene.get_ships():
                    if ship.state != "returning":
                        ship.set_state("returning")                
                
                self.scene.sm.transition(levelstates.CinematicState(self.scene))
                self.mothership = bossmothership.BossMothership(self.scene, V2(game.Game.inst.game_resolution.x * 0.75, -20))
                self.scene.flowfield.boss = self.mothership
                self.scene.enemy.mothership = self.mothership
                self.scene.game_group.add(self.mothership)
                all_planets_by_x = sorted(self.scene.get_planets(), key=lambda p:p.x, reverse=True)
                self.mothership.planets_to_revive = all_planets_by_x[0:len(all_planets_by_x) // 2]

        if self.phase == PHASE_2:
            if self.mothership.health <= 0:
                self.mothership.kill()
                self.scene.paused = True
                self.scene.sm.transition(levelstates.BeatGameState(self.scene))
