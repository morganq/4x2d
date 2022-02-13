import arrow
import asteroid
import game
import joystickcursor
import orderpanel
import planet
import pygame
import rangeindicator
import selector
import simplesprite
import sound
import spaceobject
import states
import text
from button import Button
from colors import *
from helper import *
from planet import planetpanel

V2 = pygame.math.Vector2

from multiplayer import upgradepanel


def position_panel(panel, civ):
    if civ.pos.y < 200:
        panel.pos = civ.pos
    else:
        panel.pos = civ.pos + V2(0,40 - panel.height)
    if panel.x + panel.width > game.Game.inst.game_resolution.x:
        panel.x = game.Game.inst.game_resolution.x - panel.width
    panel._reposition_children()

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
            if inp == "game_speed":
                self.scene.player_game_speed_inputs[self.civ] = 1         
            elif inp == "un_game_speed":
                self.scene.player_game_speed_inputs[self.civ] = 0
        elif self.input_mode == 'joystick':
            self.joystick_input(inp, event)
            if inp == "game_speed":
                self.scene.player_game_speed_inputs[self.civ] = 1
            elif inp == "un_game_speed":
                self.scene.player_game_speed_inputs[self.civ] = 0

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
                    position_panel(self.current_panel, self.civ)
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
            pid = self.scene.get_player_id(self.civ)
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos[pid], color=self.civ.color, player_id=pid)
            self.scene.ui_group.add(self.joystick_overlay)

    def mouse_input(self, input, event):
        if input == "menu":
            self.scene.menu_pause(self.civ)

        return super().mouse_input(input, event)

    def joystick_input(self, input, event):
        if input == "menu":
            self.scene.menu_pause(self.civ)

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
                            position_panel(self.current_panel, self.civ)
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
        position_panel(self.panel, self.civ)
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
        #sound.play("click1")
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
        if input == "menu":
            self.scene.menu_pause(self.civ)

        if input == "click":
            pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
            if not pr.collidepoint(event.gpos):
                self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))
        return super().mouse_input(input, event)

    def joystick_input(self, input, event):
        if input == "menu":
            self.scene.menu_pause(self.civ)

        if input == "back":
            self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

        if input == "confirm":
            self.panel.on_launch_click()
        return super().joystick_input(input, event)

    def get_joystick_cursor_controls(self):
        controls = list(self.panel.sliders.values())
        return [[c] for c in controls]

def apply_upgrade_with_target(civ, up, targets):
    up().apply(*targets)
    civ.register_research(up.name)
    civ.upgrades.append(up)
    civ.upgrades_stocked.pop(0)
    civ.clear_offers()

class UpgradeState(MultiplayerState):
    is_basic_joystick_panel = True
    def enter(self):
        self.hover_filter = self.filter_only_panel_ui
        res = self.civ.upgrades_stocked[0]
        uppos = self.civ.pos + V2(3,3)
        if self.civ.pos.y > 200:
            uppos = uppos + V2(0, - 80)
        ups = self.civ.offer_upgrades(res)
        self.panel = upgradepanel.UpgradePanel(uppos, self.civ, ups, res, self.on_select, self.on_reroll)
        position_panel(self.panel, self.civ)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.fade_in()
        if self.input_mode == "joystick":
            self.set_joystick_input()
        return super().enter()

    def get_joystick_cursor_controls(self):
        return self.panel.joystick_controls

    def exit(self):
        self.panel.kill()
        return super().exit()

    def on_select(self, up):
        if up.cursor is None:
            try:
                apply_upgrade_with_target(self.civ, up, [self.civ])
            except Exception as e:
                print(e)
            self.scene.finish_player_upgrade(self.civ)
            self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))
        else:
            self.scene.get_civ_sm(self.civ).transition(UpgradeTargetState(self.scene, self.civ, self.input_mode, up))

    def on_reroll(self):
        print("reroll")

    def on_back(self): # Should back if you click off the panel or press back on joy
        self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

    def mouse_input(self, input, event):
        if input in ["back","menu","rightclick"]:
            self.on_back()
        return super().mouse_input(input, event)

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])
        if input == "confirm":
            self.joystick_overlay.confirm()  
        if input == "back":
            self.on_back()


class UpgradeTargetState(MultiplayerState):
    NEARBY_RANGE = 70
    def __init__(self, scene, civ, input_mode, up):
        super().__init__(scene, civ, input_mode)
        self.up = up
        self.cursors_remaining = [up.cursor]
        if isinstance(up.cursor, list):
            self.cursors_remaining = up.cursor[::]
        self.current_cursor = None
        self.cursor_icon = None
        self.targets = []
        self.extras = []

    def filter_my_planets(self, x):
        return (
            x.get_selection_info() and
            x.get_selection_info()['type'] == 'planet' and
            x.owning_civ == self.civ and 
            x.upgradeable and
            x.is_buildable()
        )

    def filter_any_planets(self, x):
        return (
            x.get_selection_info() and
            x.get_selection_info()['type'] == 'planet'
        )        

    def filter_my_fleets(self, x):
        return (
            x.get_selection_info() and x.get_selection_info()['type'] == 'fleet' and x.owning_civ == self.civ
        )

    def next_cursor(self):
        if not self.cursors_remaining:
            apply_upgrade_with_target(self.civ, self.up, self.targets)
            self.scene.finish_player_upgrade(self.civ)
            self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))
            return
        self.current_cursor = self.cursors_remaining.pop(0)

        if self.cursor_icon:
            self.cursor_icon.kill()

        if self.joystick_overlay:
            self.joystick_overlay.set_button_options(["[*x*] Apply Upgrade"])

        if self.current_cursor == "allied_planet":
            self.cursor_icon = simplesprite.SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.hover_filter = self.filter_my_planets
            #self.selection_info_text = text.Text("Select one of your Planets to apply upgrade", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        if self.current_cursor == "any_planet":
            self.cursor_icon = simplesprite.SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.hover_filter = self.filter_any_planets
        elif self.current_cursor == "allied_fleet":
            self.scene.fleet_managers[self.civ].generate_selectable_objects()
            self.cursor_icon = simplesprite.SimpleSprite(V2(0,0), "assets/i-fleet-cursor.png")
            self.hover_filter = self.filter_my_fleets
            #self.selection_info_text = text.Text("Select one of your Fleets to apply upgrade", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        elif self.current_cursor == "point":
            self.cursor_icon = simplesprite.SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.hover_filter = self.filter_only_ui
            #self.selection_info_text = text.Text("Select a point", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        elif self.current_cursor == "nearby":
            self.cursor_icon = simplesprite.SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.range = rangeindicator.RangeIndicator(self.targets[0].pos, self.NEARBY_RANGE, PICO_LIGHTGRAY)
            self.scene.ui_group.add(self.range)
            self.extras.append(self.range)
            self.hover_filter = self.filter_only_ui
            #self.selection_info_text = text.Text("Select a point nearby", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)

        self.cursor_icon.offset = (0.5, 0.5)
        self.cursor_icon._recalc_rect()
        self.scene.ui_group.add(self.cursor_icon)            

    def on_back(self):
        self.scene.get_civ_sm(self.civ).transition(UpgradeState(self.scene, self.civ, self.input_mode))

    def enter(self):
        if self.input_mode == "joystick":
            self.set_joystick_input()           
        self.next_cursor()
        return super().enter()

    def exit(self):
        if self.cursor_icon:
            self.cursor_icon.kill()
        if self.joystick_overlay:
            self.joystick_overlay.kill()
        for extra in self.extras:
            extra.kill()

    def mouse_input(self, input, event):
        handled = super().mouse_input(input, event)
        if handled:
            return
        if self.cursor_icon:
            if input in ["mouse_move", "mouse_drag"]:
                self.cursor_icon.pos = event.gpos + V2(10,10)

        if input == "rightclick":
            self.on_back()

        if self.current_cursor:
            if input == "menu":
                self.on_back()

            if input == "click" and self.hover_sprite:
                sel = self.hover_sprite.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and self.hover_sprite.owning_civ == self.civ:
                        self.targets.append(self.hover_sprite)
                        self.next_cursor()
                        return

                    if self.current_cursor == "any_planet" and sel['type'] == "planet":
                        self.targets.append(self.hover_sprite)
                        self.next_cursor()
                        return

                    if self.current_cursor == "allied_fleet" and sel['type'] == "fleet":
                        self.targets.append(self.hover_sprite)
                        self.scene.fleet_managers[self.civ].destroy_selectable_objects()
                        self.next_cursor()
                        return

            if input == "click" and self.current_cursor == "point":
                self.targets.append(event.gpos)
                self.next_cursor()
                return

            if input == "click" and self.current_cursor == "nearby":
                if (event.gpos - self.targets[0].pos).length_squared() < self.NEARBY_RANGE ** 2:
                    self.targets.append(event.gpos)
                    self.next_cursor()
                    return                

        else:
            if input == "menu" or input == "rightclick":
                self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

    def joystick_input(self, input, event):
        if input == "back":
            self.scene.get_civ_sm(self.civ).transition(CursorState(self.scene, self.civ, self.input_mode))

        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "confirm":
            spr = self.joystick_overlay.nearest_obj
            if spr:
                sel = spr.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and spr.owning_civ == self.civ:
                        self.targets.append(spr)
                        self.next_cursor()
                        return

                    if self.current_cursor == "any_planet" and sel['type'] == "planet":
                        self.targets.append(spr)
                        self.next_cursor()
                        return                         

                    if self.current_cursor == "allied_fleet" and sel['type'] == "fleet":
                        self.scene.fleet_managers[self.civ].destroy_selectable_objects()
                        self.targets.append(spr)
                        self.next_cursor()
                        return

            if self.current_cursor == "point":
                self.targets.append(self.joystick_overlay.cursor_pos)
                self.next_cursor()
                return

            if self.current_cursor == "nearby":
                if (self.joystick_overlay.cursor_pos - self.targets[0].pos).length_squared() < self.NEARBY_RANGE ** 2:
                    self.targets.append(self.joystick_overlay.cursor_pos)
                    self.next_cursor()
                    return      

    def joystick_update(self, dt):
        all_sprites = []
        all_sprites.extend(
            sorted(self.scene.ui_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )        
        all_sprites.extend(
            sorted(self.scene.game_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and isinstance(s, spaceobject.SpaceObject) and self.hover_filter(s)]

        nearest, d = get_nearest(self.joystick_overlay.cursor_pos, selectable_sprites)
        if d < 40 ** 2:
            self.joystick_overlay.set_nearest(nearest)
        else:
            self.joystick_overlay.set_nearest(None)  

    def set_joystick_input(self):
        if not self.joystick_overlay:
            pid = self.scene.get_player_id(self.civ)
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos[pid], color=self.civ.color, player_id=pid)
            self.scene.ui_group.add(self.joystick_overlay)

class NoInputState(MultiplayerState):
    pass

class MenuState(MultiplayerState):
    is_basic_joystick_panel = True
    def enter(self):
        self.panel = self.scene.sm.state.panel
        if self.input_mode == "joystick":
            self.set_joystick_input()
        return super().enter()

    def joystick_input(self, input, event):
        if input == "menu":
            self.scene.menu_unpause()
        return super().joystick_input(input, event)

    def get_joystick_cursor_controls(self):
        return [[b] for b in self.panel.get_controls_of_type(Button)]

    def mouse_input(self, input, event):
        if input == "menu":
            self.scene.menu_unpause()        
        return super().mouse_input(input, event)
