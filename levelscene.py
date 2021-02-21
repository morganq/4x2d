from simplesprite import SimpleSprite
import sys
import traceback

import pygame

import game
import levelstates
import scene
import states
from background import Background
from civ import PlayerCiv, Civ
from meter import Meter
from button import Button
from text import Text
from colors import *
from economy import RESOURCES, Resources, RESOURCE_COLORS
from planet.planet import Planet
from resources import resource_path
from ships.ship import Ship
from v2 import V2


class LevelScene(scene.Scene):
    def __init__(self, game, options=None):
        scene.Scene.__init__(self, game)
        self.options = options
        self.animation_timer = 0
        self.my_civ = PlayerCiv()

        self.paused = False

    def load(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()

        self.background_group.add(Background(V2(0,0)))
        p = Planet(self, V2(150, 130), 5, Resources(70, 20, 10))
        p.change_owner(Civ())
        self.game_group.add(p)
        self.game_group.add(Planet(self, V2(350, 180), 8, Resources(50, 50, 0)))
        self.game_group.add(Planet(self, V2(30, 200), 8, Resources(50, 50, 0)))
        homeworld = Planet(self, V2(90, 240), 7, Resources(100, 0, 0))
        homeworld.population = 7
        homeworld.change_owner(self.my_civ)
        homeworld.ships = {'fighter':5}
        self.game_group.add(homeworld)

        self.meters = {}
        self.upgrade_texts = {}
        for i,r in enumerate(self.my_civ.resources.data.keys()):
            self.meters[r] = Meter(V2(15,3 + i * 14), 120, 9, RESOURCE_COLORS[r], self.my_civ.upgrade_limits.data[r])
            self.meters[r].stay = True
            self.ui_group.add(SimpleSprite(V2(2,2 + i * 14), "assets/i-%s.png" % r))
            self.ui_group.add(self.meters[r])
            self.upgrade_texts[r] = Text("", "small", V2(140, 4 + i * 14), multiline_width=200)
            self.ui_group.add(self.upgrade_texts[r])

        self.my_civ.resources.on_change(self.on_civ_resource_change)

        self.upgrade_button = Button(V2(game.RES[0] / 2, 296), "UPGRADE", "big", self.on_click_upgrade)
        self.upgrade_button.offset = (0.5, 1)
        self.upgrade_button._recalc_rect()
        self.upgrade_button.visible = 0
        self.ui_group.add(self.upgrade_button)

        if self.options == "upgrade":
            self.my_civ.resources.set_resource("iron", 50)        

    def on_click_upgrade(self):
        self.sm.transition(levelstates.UpgradeState(self))

    def on_civ_resource_change(self, res_type, val):
        while val >= self.my_civ.upgrade_limits.data[res_type]:
            self.my_civ.upgrades.append(res_type)
            self.my_civ.resources.data[res_type] -= self.my_civ.upgrade_limits.data[res_type]
            self.my_civ.upgrade_limits.data[res_type] += 25
        self.meters[res_type].max_value = self.my_civ.upgrade_limits.data[res_type]
        self.meters[res_type].value = self.my_civ.resources.data[res_type]

    def get_civ_ships(self, civ):
        return [s for s in self.game_group.sprites() if isinstance(s,Ship) and s.owning_civ == civ]

    def get_starting_state(self):
        return levelstates.PlayState(self)

    def initialize_state(self):
        self.sm = states.Machine(self.get_starting_state())        

    def update_layers(self):
        pass

    def start(self):
        self.load()
        self.initialize_state()      
        #sound.play_music('game')  

    def update(self, dt):
        scene.Scene.update(self, dt)
        if not self.paused:
            for sprite in self.game_group.sprites():
                sprite.update(dt)

            for sprite in self.ui_group.sprites():
                sprite.update(dt)

        colliders = [s for s in self.game_group.sprites() if s.collidable]
        lc = len(colliders)
        for i in range(lc):
            for j in range(i + 1, lc):
                d = colliders[i].pos - colliders[j].pos
                if d.sqr_magnitude() <= (colliders[i].collision_radius + colliders[j].collision_radius) ** 2:
                    colliders[i].collide(colliders[j])
                    colliders[j].collide(colliders[i])

        if len(self.my_civ.upgrades) > 0:
            self.upgrade_button.visible = True
        else:
            self.upgrade_button.visible = False

        for res_type in self.my_civ.resources.data.keys():
            num = len([u for u in self.my_civ.upgrades if u == res_type])
            if num > 0:
                self.upgrade_texts[res_type].set_text("%d upgrade%s available!" % (num, "s" if num > 1 else ""))
            else:
                self.upgrade_texts[res_type].set_text("")

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)
