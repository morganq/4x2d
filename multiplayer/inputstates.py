import arrow
import asteroid
import joystickcursor
import orderpanel
import planet
import pygame
import selector
import sound
import states
import text
from colors import *
from helper import *
from planet import planetpanel
from v2 import V2

# TODO: civ and input mode into one shared object?

class MultiplayerState(states.UIEnabledState):
    def __init__(self, scene, civ, input_mode):
        super().__init__(scene)
        self.civ = civ
        self.input_mode = input_mode

    def update(self, dt):
        if self.input_mode == "joystick":
            self.joystick_update(dt)
        else:
            self.mouse_update(dt)        

        super().update(dt)

    def take_input(self, inp, event):
        if self.input_mode == 'mouse':
            self.mouse_input(inp, event)
        elif self.input_mode == 'joystick':
            self.joystick_input(inp, event)

    def joystick_update(self, dt):
        pass

    def mouse_update(self, dt):
        pass

    def set_joystick_input(self):
        if self.is_basic_joystick_panel:
            if not self.joystick_overlay:
                controls = self.get_joystick_cursor_controls()
                self.joystick_overlay = joystickcursor.JoystickPanelCursor(self.scene, controls)
                self.scene.ui_group.add(self.joystick_overlay)       

# States that the player inputs can be in
class CursorState(MultiplayerState):
    def __init__(self, scene, civ, input_mode):
        super().__init__(scene, civ, input_mode)
        self.joystick_overlay = None

    def enter(self):
        states.UIEnabledState.enter(self)
        self.selector = None # Selection object
        self.arrow = None # Order object
        self.current_panel = None
        self.mouse_pos = V2(0,0)
        self.joy_controls_state = "default"
        self.joy_hover_filter = self.default_joy_hover_filter
        self.joy_arrow_from = None
        self.options_text = text.Text("", "small", V2(0,0), PICO_PINK, multiline_width=200, shadow=PICO_BLACK, center=False)
        self.scene.ui_group.add(self.options_text)
        if self.input_mode == "joystick":
            self.set_joystick_input()

    def exit(self):
        if self.selector:
            self.selector.kill()
        if self.arrow:
            self.arrow.kill()
        if self.current_panel:
            self.current_panel.kill()
        if self.joystick_overlay:
            self.joystick_overlay.kill()
        self.options_text.kill()
        super().exit()

    def deselect(self):
        self.last_clicked_sprite = None
        if self.current_panel:
            self.current_panel.kill()
            self.current_panel = None

    def release_drag(self):
        # Just made an order
        if self.dragging_from_sprite and self.dragging_from_sprite.get_selection_info() and self.dragging_from_sprite.owning_civ == self.civ:
            if self.hover_sprite and self.dragging_from_sprite != self.hover_sprite:
                target_selection = self.hover_sprite.get_selection_info()
                if target_selection:
                    if target_selection['type'] in ['planet', 'boss']:
                        self.scene.get_civ_sm(self.civ).transition(OrderShipsState(self.scene, self.civ, self.input_mode, self.dragging_from_sprite, self.hover_sprite))
                        self.hover_sprite.on_mouse_exit(V2(0,0))
                        self.hover_sprite = None
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

                    if target_selection['type'] == 'asteroid':
                        self.scene.get_civ_sm(self.civ).transition(OrderShipsState(self.scene, self.civ, self.input_mode, self.dragging_from_sprite, self.hover_sprite))
                        self.hover_sprite.on_mouse_exit(V2(0,0))
                        self.hover_sprite = None
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)          

    def mouse_update(self, dt):
        self.options_text.pos = self.mouse_pos + V2(8, -8)
        # Hover planet info
        # TODO: optimize?
        options = ""
        if (
            self.hover_sprite and
            isinstance(self.hover_sprite, planet.planet.Planet) and 
            not self.current_panel
        ):
            if self.hover_sprite.owning_civ == self.civ:
                options = "[*left*] Planet Info\n[*drag*] Order Ships"
            else:
                options = "[*left*] Planet Info"

        if self.last_clicked_sprite:
            selection_info = self.last_clicked_sprite.get_selection_info()
            if selection_info and selection_info['type'] == 'planet':
                if self.current_panel and self.current_panel.panel_for != self.last_clicked_sprite:
                    self.current_panel.kill()
                    self.current_panel = None


                just_update = True #self.last_clicked_sprite.needs_panel_update
                if self.current_panel and just_update:
                    self.last_clicked_sprite.needs_panel_update = False
                    self.current_panel.kill()
                    self.current_panel = None                    

                if not self.current_panel:
                    self.current_panel = planetpanel.PlanetPanel(self.last_clicked_sprite, pov_civ = self.civ)
                    self.current_panel.position_nicely(self.scene)
                    self.current_panel.add_all_to_group(self.scene.ui_group)
                    if not just_update:
                        sound.play("panel")
                        self.current_panel.fade_in()

                if self.selector:
                    self.selector.visible = 1
                    if self.selector.object != self.last_clicked_sprite:
                        self.selector.change_selection(self.last_clicked_sprite)
                else:
                    self.selector = selector.Selector(self.last_clicked_sprite)
                    self.scene.ui_group.add(self.selector)
        else:
            if self.selector:
                self.selector.visible = 0

        if self.dragging_from_sprite:
            selection_info = self.dragging_from_sprite.get_selection_info()
            if selection_info and selection_info['type'] == 'planet' and self.dragging_from_sprite.owning_civ == self.civ:
                if not self.arrow:
                    self.arrow = arrow.OrderArrow()
                    self.scene.ui_group.add(self.arrow)
                dragging_to_sprite = None
                if self.hover_sprite:
                    dragging_to_sprite = self.hover_sprite
                    sel = dragging_to_sprite.get_selection_info()
                    if not sel or sel['type'] not in ['planet', 'asteroid', 'boss']:
                        dragging_to_sprite = None
                self.arrow.setup(self.dragging_from_sprite, self.dragging_to, dragging_to_sprite)
                if self.arrow.visible:
                    self.deselect()
        else:
            if self.arrow:
                self.arrow.visible = False    

        self.scene.fleet_managers[self.civ].update_fleet_markers(self.mouse_pos)
        if self.scene.fleet_managers[self.civ].fleet_markers:
            options = "[*right*] Recall Ships"

        if self.arrow and self.arrow.visible:
            options = ""
            
        self.options_text.set_text(options)

    def take_input(self, inp, event):
        if inp == "rightclick":
            self.scene.fleet_managers[self.civ].point_recall(event.gpos)
        if inp == "mouse_move":
            self.mouse_pos = event.gpos
        if inp == "mouse_drag":
            self.mouse_pos = event.gpos

        super().take_input(inp, event)  

    def default_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet)# or isinstance(x, upgrade.upgradeicon.UpgradeIcon)

    def target_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet) or isinstance(x, asteroid.Asteroid)

    def joystick_update(self, dt):
        all_sprites = []
        all_sprites.extend(
            sorted(self.scene.ui_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )        
        all_sprites.extend(
            sorted(self.scene.game_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and self.joy_hover_filter(s)]
        if self.joy_controls_state == "default":
            self.scene.fleet_managers[self.civ].update_fleet_markers(self.joystick_overlay.cursor_pos)

        nearest, d = get_nearest(self.joystick_overlay.cursor_pos, selectable_sprites)
        if d < 40 ** 2:
            self.joystick_overlay.set_nearest(nearest)
        else:
            self.joystick_overlay.set_nearest(None)
            nearest = None

        if self.joy_controls_state == "default":
            if isinstance(nearest, planet.planet.Planet):
                if nearest.owning_civ == self.civ:
                    self.joystick_overlay.set_button_options(["[*x*] Planet Info", "[*square*] Order Ships"])
                else:
                    self.joystick_overlay.set_button_options(["[*x*] Planet Info"])
            else:
                self.joystick_overlay.set_button_options([])
        elif self.joy_controls_state == "arrow":
            if nearest:
                self.joystick_overlay.set_button_options(["[*x*] Select Target", "[*circle*] Cancel"])
            else:
                self.joystick_overlay.set_button_options(["[*circle*] Cancel"])

        if self.current_panel and self.current_panel.panel_for != self.joystick_overlay.nearest_obj:
            self.current_panel.kill()
            self.current_panel = None

        if self.joy_controls_state == "arrow":
            self.arrow.setup(self.joy_arrow_from, self.joystick_overlay.cursor_pos, self.joystick_overlay.nearest_obj)

    def set_mouse_input(self):
        pass

    def set_joystick_input(self):
        if not self.joystick_overlay:
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos)
            self.scene.ui_group.add(self.joystick_overlay)

    def joystick_input(self, input, event):
        print("joystick_input", input, event)
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "special" and len(self.civ.upgrades_stocked) > 0:
            self.scene.player_click_upgrade(self.civ)

        if input == "confirm":
            if self.joy_controls_state == "default":
                spr = self.joystick_overlay.nearest_obj
                if spr:
                    # Check if we clicked a stored upgrade
                    #if isinstance(spr, upgrade.upgradeicon.UpgradeIcon):
                    #    spr.on_mouse_down(spr.pos)

                    # Otherwise...
                    selection_info = spr.get_selection_info()
                    if selection_info and selection_info['type'] == 'planet':
                        if self.current_panel and self.current_panel.panel_for != spr:
                            self.current_panel.kill()
                            self.current_panel = None

                        just_update = True #spr.needs_panel_update
                        if self.current_panel and just_update:
                            spr.needs_panel_update = False
                            self.current_panel.kill()
                            self.current_panel = None                    

                        if not self.current_panel:
                            self.current_panel = planetpanel.PlanetPanel(spr, pov_civ = self.civ)
                            self.current_panel.position_nicely(self.scene)
                            self.current_panel.add_all_to_group(self.scene.ui_group)
                            if not just_update:
                                sound.play("panel")
                                self.current_panel.fade_in()

                        if self.selector:
                            self.selector.visible = 1
                            if self.selector.object != spr:
                                self.selector.change_selection(spr)
                        else:
                            self.selector = selector.Selector(spr)
                            self.scene.ui_group.add(self.selector)

            elif self.joy_controls_state == "arrow":
                spr = self.joystick_overlay.nearest_obj
                if spr:
                    target_selection = spr.get_selection_info()
                    if spr != self.joy_arrow_from and target_selection:
                        if target_selection['type'] in ['planet', 'boss', 'asteroid']:
                            self.scene.get_civ_sm(self.civ).transition(OrderShipsState(self.scene, self.civ, self.input_mode, self.joy_arrow_from, spr))
                            spr.on_mouse_exit(V2(0,0))

        if input == "action":
            if self.joy_controls_state == "default":
                spr = self.joystick_overlay.nearest_obj
                if spr and spr.owning_civ == self.civ:
                    self.joy_controls_state = "arrow"
                    self.arrow = arrow.OrderArrow()
                    self.scene.ui_group.add(self.arrow)
                    self.arrow.setup(spr, self.joystick_overlay.cursor_pos, None)
                    self.deselect()
                    self.joy_arrow_from = spr
                    self.joy_hover_filter = self.target_joy_hover_filter

        if input == "back":
            if self.joy_controls_state == "arrow":
                self.joy_controls_state = "default"
                self.joy_hover_filter = self.default_joy_hover_filter
                self.arrow.visible = False
            elif self.current_panel:
                self.current_panel.kill()
                self.current_panel = None
            else:
                self.scene.fleet_managers[self.civ].point_recall(self.joystick_overlay.cursor_pos)


class OrderShipsState(MultiplayerState):
    is_basic_joystick_panel = True    
    def __init__(self, scene, civ, input_mode, planet_from, planet_to, path=None):
        MultiplayerState.__init__(self, scene, civ, input_mode)
        self.civ = civ
        self.planet_from = planet_from
        self.planet_to = planet_to
        self.path = path
        self.joystick_overlay = None

    def deselect(self):
        pass

    def enter(self):
        self.hover_filter = self.filter_only_panel_ui
        self.panel = orderpanel.OrderPanel(V2(0,0), self.planet_from, self.planet_to, self.on_order)
        self.panel.position_nicely(self.scene)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.fade_in()
        self.arrow = arrow.OrderArrow()
        self.scene.ui_group.add(self.arrow)
        self.arrow.setup(self.planet_from, None, self.planet_to)
        sound.play("attackpanel")
        if self.input_mode == "joystick":
            self.set_joystick_input()        
        super().enter()

    def exit(self):
        self.hover_filter = lambda x: True
        self.panel.kill()
        self.arrow.kill()
        if self.joystick_overlay:
            self.joystick_overlay.kill()
        sound.play("click1")
        super().exit()

    def on_order(self, values):
        for ship,num in values.items():
            if ship == "colonist":
                self.planet_from.emit_ship(ship, {"to":self.planet_to, "path":self.path, "num":num})
            else:
                for i in range(num):
                    self.planet_from.emit_ship(ship, {"to":self.planet_to, "path":self.path})
        self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

    def mouse_input(self, input, event):
        if input == "click":
            pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
            if not pr.collidepoint(event.gpos.tuple()):
                self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))
        return super().mouse_input(input, event)

    def joystick_input(self, input, event):
        if input == "back":
            self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

        if input == "confirm":
            self.panel.on_launch_click()
        return super().joystick_input(input, event)

    def get_joystick_cursor_controls(self):
        controls = list(self.panel.sliders.values())
        return [[c] for c in controls]

class UpgradeState(MultiplayerState):
    pass
