import fleet
import flowfield
import game
import sound
from aliens import alien
from civ import Civ
from helper import get_nearest
from levelscene import LevelScene
from v2 import V2

from tutorial.tutorialmessage import TutorialMessage


class TutorialScene(LevelScene):
    def __init__(self, game):
        super().__init__(game, None, None, 1)
        self.tut_text_number = 0
        self.is_tutorial = True

    def time_edge(self, time, dt):
        if self.time < time and self.time + (dt * self.game_speed) >= time:
            return True
        return False

    def set_tutorial_text(self, text, number, offset=None):
        if self.tut_text_number >= number:
            return
        if text == self.tutorial_panel.text._text:
            return
        self.tut_text_number = number
        if text:
            self.tutorial_panel.set_text(text)
            if offset:
                self.tutorial_panel.pos = V2(game.RES[0] / 2 - 172, game.RES[1] - 54) + offset
            else:
                self.tutorial_panel.pos = V2(game.RES[0] / 2 - 172, game.RES[1] - 54)
            self.tutorial_panel._reposition_children()                
            self.tutorial_panel.set_visible(True)
            self.tutorial_panel.fade_in()
            sound.play("static")
        else:
            self.tutorial_panel.set_text("")
            self.tutorial_panel.set_visible(False)

    def setup_players(self):
        # Me
        self.homeworld = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.my_civ))[0]

        # Alien
        p = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.enemy.civ))[0]
        self.alien_homeworld = p

    def load_level(self, levelfile):
        return

    def load(self):
        self.create_layers()
        AlienClass = alien.ALIENS['tutorial']
        self.enemies = [AlienClass(self, Civ(self))]
        self.enemy = self.enemies[0]        
        
        self.load_level(None)

        self.setup_players()
        self.my_civ.upkeep_enabled = False
        self.add_ui_elements()

        self.tutorial_panel = TutorialMessage(" ")
        self.tutorial_panel.pos = V2(game.RES[0] / 2 - 172, game.RES[1] - 54)
        self.ui_group.add(self.tutorial_panel)
        self.tutorial_panel.add_all_to_group(self.ui_group)
        self.tutorial_panel._reposition_children()
        self.tutorial_panel.set_visible(False)

        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])

        self.fleet_managers = {
            'my':fleet.FleetManager(self, self.my_civ),
            'enemy':fleet.FleetManager(self, self.enemy.civ)
        }

        self.flowfield = flowfield.FlowFieldMap()
        self.flowfield.generate(self)
        self.flowfielddebug = 0

        self.enemy.set_difficulty(1)
