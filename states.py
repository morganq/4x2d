from random import randint
from v2 import V2
import pygame
import framesprite
import helper

class Machine:
    def __init__(self, state):
        self.state = state
        if self.state:
            self.state.enter()

    def transition(self, other):
        if self.state:
            self.state.exit()
        self.state = other
        self.state.enter()

class State:
    def __init__(self, scene):
        self.scene = scene

    def take_input(self, input, event):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass

class UIEnabledState(State):
    def __init__(self, scene):
        State.__init__(self, scene)
        self.hover_filter = lambda x: True
        self.hover_sprite = None # Mouse is over this one
        self.clicking_sprite = None # Currently mouse-down-ing this one
        self.last_clicked_sprite = None # Last clicked, clears when clicking on nothing
        self.dragging_from_sprite = None # When dragging, this is the sprite dragging FROM
        self.dragging_to = None # When dragging, this is the position dragging TO        

        self.key_picked_sprite = None
        self.key_images = {}
        self.key_targets = {}
        self.key_crosshair = None

    def filter_only_panel_ui(self, o):
        if hasattr(self.panel, "tree_children"):
            if o in self.panel.tree_children:
                return True
        return o in [c['control'] for c in self.panel._controls]

    def enter(self):
        for i,d in enumerate(['up', 'right', 'down', 'left']):
            self.key_images[d] = framesprite.FrameSprite(V2(0,0), 'assets/keyarrows.png',9)
            self.key_images[d].frame = i
            self.scene.ui_group.add(self.key_images[d])
            self.scene.ui_group.change_layer(self.key_images[d],3)
            self.key_images[d].visible = False
        self.key_crosshair = framesprite.FrameSprite(V2(0,0), 'assets/keyarrows.png',9)
        self.key_crosshair.frame = 4
        self.scene.ui_group.add(self.key_crosshair)
        self.scene.ui_group.change_layer(self.key_crosshair,3)


    def deselect(self):
        pass

    def release_drag(self):
        pass

    def filter_only_ui(self, o):
        return o in self.scene.ui_group.sprites()

    def set_keyboard_input(self):
        self.scene.game.input_mode = 'keyboard'
        for i,d in enumerate(['up', 'right', 'down', 'left']):
            self.key_images[d].visible = True
        self.key_crosshair.visible = True
        self.update_key_targets()

    def set_mouse_input(self):
        self.scene.game.input_mode = 'mouse'
        for i,d in enumerate(['up', 'right', 'down', 'left']):
            self.key_images[d].visible = False        
        self.key_crosshair.visible = False

    def take_input(self, input, event):
        if input in ["mouse_move", "mouse_drag", "click", "unclick"]:
            self.set_mouse_input()
        elif input in ['left', 'right', 'up', 'down']:
            self.set_keyboard_input()
        if self.scene.game.input_mode == 'mouse':
            self.mouse_input(input,event)
        elif self.scene.game.input_mode == 'keyboard':
            self.keyboard_input(input, event)

    def mouse_input(self, input, event):
        all_sprites = self.scene.game_group.sprites()[::]
        all_sprites.extend(self.scene.ui_group.sprites()[::])
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and self.hover_filter(s)]
        selectable_sprites.sort(key=lambda x:x.layer, reverse=True) 
        is_mouse_event = False
        if input in ["mouse_move", "mouse_drag", "click", "unclick"]:
            is_mouse_event = True

        if is_mouse_event:
            mx, my = event.gpos.x, event.gpos.y
            sprite_found = None
            for sprite in selectable_sprites:
                if (mx >= sprite.rect[0] and
                    mx <= sprite.rect[0] + sprite.rect[2] and
                    my >= sprite.rect[1] and
                    my <= sprite.rect[1] + sprite.rect[3]):
                    sprite_found = sprite
                    break
            
            if input in ["mouse_move", "mouse_drag"]:
                #if not self.clicking_sprite:
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

                if input == "mouse_drag" and self.clicking_sprite:
                    self.dragging_from_sprite = self.clicking_sprite
                    self.dragging_to = event.gpos
                    self.clicking_sprite.on_drag(event.gpos)

            if input == "click":
                if self.hover_sprite:
                    self.hover_sprite.on_mouse_down(event.gpos)
                    self.clicking_sprite = self.hover_sprite
                    self.last_clicked_sprite = self.clicking_sprite
                else:
                    self.deselect()
            
            if input == "unclick":
                if self.clicking_sprite:
                    self.clicking_sprite.on_mouse_up(event.gpos)
                    self.clicking_sprite = None
                if self.dragging_from_sprite:
                    self.release_drag()
                self.dragging_from_sprite = None
                self.dragging_to = None

    def update_key_targets(self):
        self.key_targets = {'left':None, 'right':None, 'up':None, 'down':None}
        sprite_directions = {'left':[], 'right':[], 'up':[], 'down':[]}
        all_sprites = self.scene.game_group.sprites()[::]
        all_sprites.extend(self.scene.ui_group.sprites()[::])
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and self.hover_filter(s)]
        for s in selectable_sprites:
            if not self.key_picked_sprite: self.key_picked_sprite = s
            self.key_crosshair.pos = self.key_picked_sprite.get_center() + V2(5,5)
            if self.key_picked_sprite == s: continue
            delta = s.pos - self.key_picked_sprite.pos
            if abs(delta.x) > abs(delta.y):
                if delta.x > 0:
                    sprite_directions['right'].append(s)
                else:
                    sprite_directions['left'].append(s)
            else:
                if delta.y > 0:
                    sprite_directions['down'].append(s)
                else:
                    sprite_directions['up'].append(s)

        for d, sl in sprite_directions.items():
            nearest = helper.get_nearest(self.key_picked_sprite, sl)[0]
            if nearest:
                self.key_targets[d] = nearest
                self.key_images[d].pos = nearest.get_center() + V2(5,5)
                self.key_images[d].visible = True
            else:
                self.key_images[d].visible = False

    def keyboard_input(self, input, event):
        sel = self.key_picked_sprite.get_selection_info()
        if sel and sel['type'] == 'slider':
            if input == 'left':
                self.key_picked_sprite.set_value(self.key_picked_sprite.value - 1)
                return
            elif input == 'right':
                self.key_picked_sprite.set_value(self.key_picked_sprite.value + 1)
                return
        for d in ['left', 'up', 'right', 'down']:
            if input == d and self.key_targets[d]:
                s = self.key_targets[d]
                self.key_picked_sprite.on_mouse_exit(self.key_picked_sprite.pos)
                self.hover_sprite = s
                self.last_clicked_sprite = s
                self.key_picked_sprite = s
                self.key_picked_sprite.on_mouse_enter(self.key_picked_sprite.pos)

        if input == 'action':
            self.key_picked_sprite.on_mouse_down(self.key_picked_sprite.pos)
            self.key_picked_sprite.on_mouse_up(self.key_picked_sprite.pos)            

    def exit(self):
        self.key_crosshair.kill()
        for d in ['left', 'up', 'right', 'down']:
            self.key_images[d].kill()

    def update(self, dt):
        if self.scene.game.input_mode == 'keyboard':
            self.update_key_targets()
        State.update(self, dt)

    def paused_update(self, dt):
        self.update(dt)