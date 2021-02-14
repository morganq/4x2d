from colors import *
import scene
import sys
import game
import levelstates
import states
import pygame
from resources import resource_path
import traceback

class LevelScene(scene.Scene):
    def __init__(self, game, level=None):
        scene.Scene.__init__(self, game)
        self.animation_timer = 0
        self.level_file = level or "empty"

    def load(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredUpdates()
        self.ui_group = pygame.sprite.Group()
        self.tutorial_group = pygame.sprite.Group()

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

        for sprite in self.game_group.sprites():
            sprite.update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)

    def take_input(self, input, event):
        all_sprites = self.game_group.sprites()[::]
        all_sprites.extend(self.ui_group.sprites()[::])
        selectable_sprites = [s for s in all_sprites if s.selectable]
        selectable_sprites.sort(key=lambda x:x.layer, reverse=True)
        is_mouse_event = False
        if input in ["mouse_move", "click", "unclick"]:
            is_mouse_event = True

        if is_mouse_event:
            mx, my = event.gpos
            sprite_found = None
            for sprite in selectable_sprites:
                if (mx >= sprite.rect[0] and
                    mx <= sprite.rect[0] + sprite.rect[2] and
                    my >= sprite.rect[1] and
                    my <= sprite.rect[1] + sprite.rect[3]):
                    sprite_found = sprite
                    break
            
            if input == "mouse_move":
                if not self.clicking_sprite:
                    if not sprite_found and self.hover_sprite: # Mouse Exit
                        self.hover_sprite.on_mouse_exit(event.gpos)
                        self.hover_sprite = None
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    if sprite_found and not self.hover_sprite: # Mouse Enter
                        self.hover_sprite = sprite_found
                        self.hover_sprite.on_mouse_enter(event.gpos)
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_HAND)
                    if sprite_found and self.hover_sprite and self.hover_sprite != sprite_found: # Mouse change focus
                        self.hover_sprite.on_mouse_exit(event.gpos)
                        self.hover_sprite = sprite_found
                        self.hover_sprite.on_mouse_enter(event.gpos)

            if input == "click":
                if self.hover_sprite:
                    self.hover_sprite.on_mouse_down(event.gpos)
                    self.clicking_sprite = self.hover_sprite
            
            if input == "unclick":
                if self.clicking_sprite:
                    self.clicking_sprite.on_mouse_up(event.gpos)
                    self.clicking_sprite = None        