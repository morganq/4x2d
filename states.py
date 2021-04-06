import pygame

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

    def filter_only_panel_ui(self, o):
        if hasattr(self.panel, "tree_children"):
            if o in self.panel.tree_children:
                return True
        return o in [c['control'] for c in self.panel._controls]

    def enter(self):
        pass

    def deselect(self):
        pass

    def release_drag(self):
        pass

    def filter_only_ui(self, o):
        return o in self.scene.ui_group.sprites()

    def take_input(self, input, event):
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