import random

import game
import menuscene
from asteroid import Asteroid
from economy import Resources
from planet.planet import Planet
from ships.colonist import Colonist
from upgrade.upgrades import UPGRADE_CLASSES
from upgradestate import UpgradeState
from v2 import V2

from tutorial.tutorialscene import TutorialScene


class Tutorial1Scene(TutorialScene):
    def load_level(self, levelfile):
        p1 = Planet(self, V2(300, 220) + self.game.game_offset, 7, Resources(70,20,10))
        p1.change_owner(self.my_civ)
        self.homeworld = p1
        self.game_group.add(p1)

        p2 = Planet(self, V2(400, 120) + self.game.game_offset, 3, Resources(100,0,0))
        p2.change_owner(self.enemy.civ)
        p2.visible = False
        p2.selectable = False
        p2.population = 0
        self.game_group.add(p2)

        for i in range(6):
            theta = i * -0.65
            pos = V2.from_angle(theta) * (50 + random.random() * 80) + self.homeworld.pos
            a = Asteroid(self, pos + self.game.game_offset, Resources(40, 0, 0))
            self.game_group.add(a)

        self.objgrid.generate_grid(self.get_objects_initial())
        

    def setup_players(self):
        super().setup_players()
        self.alien_homeworld.population = 0
        self.alien_homeworld.ships['alien1fighter'] = 0
        self.alien_homeworld.ships['alien1warpship'] = 0
        self.homeworld.ships['fighter'] = 3

    def load(self):
        super().load()
        self.my_civ.base_upgrade_limits.iron = 230
        self.o2_meter.kill()

        self.my_civ.offered_upgrades = {
            'buildings':'b_defense1',
            'ships':'s_basicfighters1',
            'tech':'t_mechanics1'
        }

        self.game.run_info.rerolls = 0

    def update(self, dt):
        if self.time_edge(1.5, dt):
            if self.game.input_mode == "joystick":
                self.set_tutorial_text("Press [*x*] on your planet to see its status and resources. Press [*square*] to order ships from a planet and send one to an asteroid.", 1)
            else:
                self.set_tutorial_text("Click your planet to see its status and resources. Drag from your planet to an asteroid to order a fighter to attack.", 1)
        ships = self.get_civ_ships(self.my_civ)
        if self.time_edge(20, dt) and len(ships) == 0:
            if self.game.input_mode == "joystick":
                self.set_tutorial_text("Try pressing [*square*] with your cursor on your planet, then moving the cursor to an asteroid.", 2)
            else:
                self.set_tutorial_text("Try dragging from your planet to an asteroid, then you can order fighters to attack it.", 2)
        if len(ships) > 0 and ships[0].time > 1:
            self.set_tutorial_text("Great! Destroy all the asteroids to collect a lot of iron!", 3)
        if len(ships) > 0 and ships[0].time > 9:
            if self.game.input_mode == "joystick":
                self.set_tutorial_text("Once you've given orders to a fleet of ships, they will follow them until complete. You can also press [*circle*] on a fleet to cancel their orders.", 3.5)
            else:
                self.set_tutorial_text("Once you've given orders to a fleet of ships, they will follow them until complete. You can also right-click on a fleet to cancel their orders.", 3.5)
        if self.my_civ.num_upgrades > 0:
            if self.game.input_mode == "joystick":
                self.set_tutorial_text(
                    "Nice work. You have enough iron now to acquire a new Upgrade! Press [*triangle*]. Get Upgrades to improve your planets, build ships, or unlock new technologies.",
                    4,
                    offset=V2(0, -50)
                )
            else:
                self.set_tutorial_text(
                    "Nice work. You have enough iron now to acquire a new Upgrade! Get Upgrades to improve your planets, build ships, or unlock new technologies.",
                    4,
                    offset=V2(0, -50)
                )
            if self.tutorial_panel.shown_time > 14:
                if self.game.input_mode == "joystick":
                    self.set_tutorial_text("Press [*triangle*] to acquire a new Upgrade.", 5,offset=V2(0, -50))
                else:
                    self.set_tutorial_text("Click the Upgrade button below.", 5,offset=V2(0, -50))
                    

        if isinstance(self.sm.state, UpgradeState):
            self.set_tutorial_text("", 6)

        if len(self.my_civ.researched_upgrade_names) > 0 and self.tut_text_number < 7:
            self.set_tutorial_text("We can also use our fighters to damage the enemy. Destroy their colony on that planet!", 7)
            self.alien_homeworld.ships['alien1fighter'] = 1
            self.alien_homeworld.visible = True
            self.alien_homeworld.selectable = True

        if len(self.get_civ_planets(self.enemy.civ)) == 0 and self.tut_text_number <= 7:
            for ship in self.get_civ_ships(self.my_civ):
                ship.set_state("returning")
            s = Colonist(self, self.homeworld.pos + V2(-90, -90), self.my_civ)
            s.set_pop(3)
            s.set_target(self.homeworld)
            self.game_group.add(s)
            self.set_tutorial_text("We're going to need workers to take control of the planet. Workers also mine resources automatically. Here comes a friendly worker ship now.", 8)

        if self.homeworld.population > 1:
            if self.tut_text_number <= 8:
                self.set_tutorial_text("Now that you have workers on this planet, mining will begin and worker population will slowly grow.", 9)
            elif self.tut_text_number == 9 and self.tutorial_panel.shown_time > 10:
                self.set_tutorial_text("Workers mine all the types of resources on the planet. For this planet, that means mainly iron, but also some ice and gas. Each resource has its own unique pool of Upgrades.", 10)
            elif self.tut_text_number == 10 and self.tutorial_panel.shown_time > 12:
                self.set_tutorial_text("The more planets you control, the more mining you'll be able to do. Take over the other planet by sending workers to it.", 11)

            
        if len(self.get_civ_planets(self.my_civ)) == 2:
            self.set_tutorial_text("Excellent! Defeating the federation comes down to making smart decisions: choosing your Upgrades, controlling planets, and dispatching ships to destroy the enemy.", 12)
            if self.tut_text_number == 12 and self.tutorial_panel.shown_time > 15:
                self.set_tutorial_text("Good luck!!", 13)
            if self.tut_text_number == 13 and self.tutorial_panel.shown_time > 5:
                self.game.scene = menuscene.MenuScene(self.game)
                self.game.scene.start()

        return super().update(dt)
