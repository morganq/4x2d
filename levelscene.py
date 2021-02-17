from colors import *
import scene
import sys
import game
import levelstates
import states
import pygame
from resources import resource_path
import traceback
from economy import Resources
from v2 import V2
from planet.planet import Planet
from civ import PlayerCiv

class LevelScene(scene.Scene):
    def __init__(self, game, level=None):
        scene.Scene.__init__(self, game)
        self.animation_timer = 0
        self.level_file = level or "empty"
        self.my_civ = PlayerCiv()

        self.paused = False

    def load(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()

        self.game_group.add(Planet(V2(150, 130), 5, Resources(70, 20, 10)))
        self.game_group.add(Planet(V2(350, 180), 8, Resources(50, 50, 0)))
        homeworld = Planet(V2(90, 240), 7, Resources(100, 0, 0))
        homeworld.population = 7
        homeworld.change_owner(self.my_civ)
        homeworld.ships = {'fighter':5, 'bomber':2, 'interceptor':1, 'destroyer':1}
        self.game_group.add(homeworld)

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


    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)