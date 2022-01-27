import pygame

import game
import joystickcursor
import levelstates
import planet
import sound
import starmap
import text
from anyupgradepanel import AnyUpgradePanel
from button import Button
from colors import *
from funnotification import FunNotification
from helper import get_nearest
from rangeindicator import RangeIndicator
from simplesprite import SimpleSprite
from spaceobject import SpaceObject
from states import State, UIEnabledState
from upgrade.upgradebutton import UpgradeButton
from upgrade.upgradeicon import UpgradeIcon
from upgrade.upgradepanel import UpgradePanel

V2 = pygame.math.Vector2


class UpgradeState(UIEnabledState):
    NEARBY_RANGE = 70
    is_basic_joystick_panel = True
    def __init__(self, scene):
        UIEnabledState.__init__(self, scene)
        self.pending_upgrade = None
        self.cursor_icon = None
        self.selection_info_text = None
        #self.back_button = None
        self.current_cursor = None

    def enter(self):
        sound.play("panel")
        self.scene.paused = True
        resource = self.scene.player_civ.upgrades_stocked[0]
        is_new_roll = len(self.scene.player_civ.offered_upgrades) == 0
        offered_upgrades = self.scene.player_civ.offer_upgrades(resource)
        self.panel = UpgradePanel(V2(0,0), offered_upgrades, resource, self.on_select, self.on_reroll, is_new_roll)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        
        self.hover_filter = self.filter_only_panel_ui
        self.selected_targets = []
        self.extras = []
        super().enter()
        self.panel.fade_in(speed=3)

    def filter_my_planets(self, x):
        return (
            x.get_selection_info() and
            x.get_selection_info()['type'] == 'planet' and
            x.owning_civ == self.scene.player_civ and 
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
            x.get_selection_info() and x.get_selection_info()['type'] == 'fleet' and x.owning_civ == self.scene.player_civ
        )

    def get_joystick_cursor_controls(self):
        l = []
        if self.panel:
            return self.panel.joystick_controls

    def exit(self):
        self.hover_filter = lambda x:True
        self.scene.paused = False
        if self.selection_info_text:
            self.selection_info_text.kill()
        if self.cursor_icon:
            self.cursor_icon.kill()
        #if self.back_button:
        #    self.back_button.kill()
        super().exit()

    def finish(self, target=None, cancel = False):
        for extra in self.extras:
            extra.kill()
        self.extras = []        
        if not cancel:
            self.scene.player_civ.upgrades_stocked.pop(0)
            self.scene.player_civ.register_research(self.pending_upgrade.name)
            self.scene.player_civ.clear_offers()
            sound.play("upgrade2")
            self.scene.pop_asset_button()
        if self.panel:
            self.panel.kill()
        if self.joystick_overlay:
            self.joystick_overlay.kill()
        self.scene.sm.transition(levelstates.PlayState(self.scene))

    def on_reroll(self):
        self.scene.player_civ.clear_offers()
        self.panel.kill()
        self.scene.game.run_info.rerolls -= 1
        resource = self.scene.player_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.player_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll, True)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in(speed=10)

        if self.joystick_overlay:
            self.joystick_overlay.kill()
            self.joystick_overlay = joystickcursor.JoystickPanelCursor(self.scene, self.get_joystick_cursor_controls())
            self.scene.ui_group.add(self.joystick_overlay)

    def setup_cursor_type(self, cursor):
        if self.joystick_overlay:
            self.joystick_overlay.kill()
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos[0])
            self.scene.ui_group.add(self.joystick_overlay)
            self.joystick_overlay.set_button_options(["[*x*] Select"])

        res = self.scene.game.game_resolution

        if self.panel:
            self.panel.kill()
        if cursor == "allied_planet":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.hover_filter = self.filter_my_planets
            self.selection_info_text = text.Text("Select one of your Planets to apply upgrade", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        elif cursor == "any_planet":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.hover_filter = self.filter_any_planets
            self.selection_info_text = text.Text("Select any Planet to apply upgrade", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)            
        elif cursor == "allied_fleet":
            self.scene.fleet_managers['my'].generate_selectable_objects()
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-fleet-cursor.png")
            self.hover_filter = self.filter_my_fleets
            self.selection_info_text = text.Text("Select one of your Fleets to apply upgrade", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        elif cursor == "point":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.hover_filter = self.filter_only_ui
            self.selection_info_text = text.Text("Select a point", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)
        elif cursor == "nearby":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.range = RangeIndicator(self.selected_targets[0].pos, self.NEARBY_RANGE, PICO_LIGHTGRAY)
            self.scene.ui_group.add(self.range)
            self.extras.append(self.range)
            self.hover_filter = self.filter_only_ui
            self.selection_info_text = text.Text("Select a point nearby", "big", V2(res.x / 2, res.y / 2), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK, flash_color=PICO_YELLOW)

        self.cursor_icon.offset = (0.5, 0.5)
        self.cursor_icon._recalc_rect()
        self.scene.ui_group.add(self.cursor_icon)
        self.selection_info_text.offset = (0.5,0.5)
        self.selection_info_text.layer = 15    
        self.scene.ui_group.add(self.selection_info_text)                             
        self.scene.pause_sprite.set_exceptions([s for s in self.scene.game_group.sprites() if self.hover_filter(s)])

    def on_select(self, upgrade):
        if isinstance(upgrade.cursor, list):
            self.cursors = upgrade.cursor[::]
        else:
            self.cursors = [upgrade.cursor]

        self.current_cursor = self.cursors.pop(0)

        if self.current_cursor == None:
            self.pending_upgrade = upgrade
            self.scene.player_civ.upgrades.append(upgrade)
            upgrade().apply(self.scene.player_civ)
            self.scene.ui_group.add(FunNotification(self.pending_upgrade.title, None))
            self.finish()
        else:
            self.pending_upgrade = upgrade
            self.setup_cursor_type(self.current_cursor)
            #self.back_button = Button(V2(game.RES[0] / 2, game.RES[1] - 5), "Back", "small", self.on_back)
            #self.back_button.offset = (0.5, 1)
            #self.scene.ui_group.add(self.back_button)            

    def next_selection_step(self):
        sound.play("click1")
        for extra in self.extras:
            extra.kill()
        self.extras = []

        if self.selection_info_text:
            self.selection_info_text.kill()
        if self.cursor_icon:
            self.cursor_icon.kill()

        if self.cursors:
            self.current_cursor = self.cursors.pop(0)
            self.setup_cursor_type(self.current_cursor)
        else:
            u = self.pending_upgrade().apply(*self.selected_targets)
            self.finish(target=self.selected_targets[0])

    def mouse_input(self, input, event):
        handled = super().mouse_input(input, event)
        if handled and input != "menu":
            return
        if self.cursor_icon:
            if input in ["mouse_move", "mouse_drag"]:
                self.cursor_icon.pos = event.gpos + V2(10,10)

        if self.current_cursor:
            if input == "menu":
                self.on_back()

            if input == "click" and self.hover_sprite:
                sel = self.hover_sprite.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and self.hover_sprite.owning_civ == self.scene.player_civ:
                        self.selected_targets.append(self.hover_sprite)
                        self.next_selection_step()
                        return

                    if self.current_cursor == "any_planet" and sel['type'] == "planet":
                        self.selected_targets.append(self.hover_sprite)
                        self.next_selection_step()
                        return                        

                    if self.current_cursor == "allied_fleet" and sel['type'] == "fleet":
                        self.selected_targets.append(self.hover_sprite)
                        self.scene.fleet_managers['my'].destroy_selectable_objects()
                        self.next_selection_step()
                        return

            if input == "click" and self.current_cursor == "point":
                self.selected_targets.append(event.gpos)
                self.next_selection_step()
                return

            if input == "click" and self.current_cursor == "nearby":
                if (event.gpos - self.selected_targets[0].pos).length_squared() < self.NEARBY_RANGE ** 2:
                    self.selected_targets.append(event.gpos)
                    self.next_selection_step()
                    return                

        else:
            if input == "menu":
                self.finish(cancel = True)

            if input == "click":
                pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
                if not pr.collidepoint(event.gpos):
                    self.finish(cancel = True)    

    def joystick_input(self, input, event):
        if input == "back":
            if self.pending_upgrade:
                sound.play("cancel")
                self.on_back()
            else:
                sound.play("cancel")
                self.finish(cancel = True)

        if self.pending_upgrade is None:
            self.joystick_overlay.controls = self.get_joystick_cursor_controls()
            return super().joystick_input(input, event)

        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "confirm":
            spr = self.joystick_overlay.nearest_obj
            if spr:
                sel = spr.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and spr.owning_civ == self.scene.player_civ:
                        self.selected_targets.append(spr)
                        self.next_selection_step()
                        return

                    if self.current_cursor == "any_planet" and sel['type'] == "planet":
                        self.selected_targets.append(spr)
                        self.next_selection_step()
                        return                           

                    if self.current_cursor == "allied_fleet" and sel['type'] == "fleet":
                        self.selected_targets.append(spr)
                        self.scene.fleet_managers['my'].destroy_selectable_objects()
                        self.next_selection_step()
                        return

            if self.current_cursor == "point":
                self.selected_targets.append(self.joystick_overlay.cursor_pos)
                self.next_selection_step()
                return

            if self.current_cursor == "nearby":
                if (self.joystick_overlay.cursor_pos - self.selected_targets[0].pos).length_squared() < self.NEARBY_RANGE ** 2:
                    self.selected_targets.append(self.joystick_overlay.cursor_pos)
                    self.next_selection_step()
                    return      

    def joystick_update(self, dt):
        if self.pending_upgrade is None:
            return

        all_sprites = []
        all_sprites.extend(
            sorted(self.scene.ui_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )        
        all_sprites.extend(
            sorted(self.scene.game_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and isinstance(s, SpaceObject) and self.hover_filter(s)]

        nearest, d = get_nearest(self.joystick_overlay.cursor_pos, selectable_sprites)
        if d < 40 ** 2:
            self.joystick_overlay.set_nearest(nearest)
        else:
            self.joystick_overlay.set_nearest(None)                              
        
    def on_back(self):
        print("on_back")
        if self.cursor_icon:
            self.cursor_icon.kill()
            self.cursor_icon = None

        self.current_cursor = None

        self.cursor_type = None
        self.pending_upgrade = None
        resource = self.scene.player_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.player_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll, False)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in(speed=10)
        self.hover_filter = self.filter_only_panel_ui
        #self.back_button.kill()
        #self.back_button = None
        self.selection_info_text.kill()
        self.selection_info_text = None
        self.selected_targets = []
        for extra in self.extras:
            extra.kill()
        self.extras = []   

        if self.joystick_overlay:
            self.joystick_overlay.kill()
            self.joystick_overlay = joystickcursor.JoystickPanelCursor(self.scene, self.get_joystick_cursor_controls())
            self.scene.ui_group.add(self.joystick_overlay)             

    def update(self, dt):
        if self.scene.game.input_mode == "joystick":
            self.joystick_update(dt)
        return super().update(dt)


class DevAnyUpgradeState(UpgradeState):
    def __init__(self, scene):
        super().__init__(scene)

    def enter(self):
        self.scene.paused = True
        self.selected_targets = []
        self.extras = []
        self.panel = AnyUpgradePanel(V2(0,0), self.on_select)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.hover_filter = self.filter_only_panel_ui
        return UIEnabledState.enter(self)

    def finish(self, target=None, cancel = False):
        for extra in self.extras:
            extra.kill()
        self.extras = []        
        if not cancel:
            self.scene.player_civ.register_research(self.pending_upgrade.name)
        if self.panel:
            self.panel.kill()
        self.scene.sm.transition(levelstates.PlayState(self.scene))        

    def on_back(self):
        return

    def get_joystick_cursor_controls(self):
        l = []
        l.extend([[c] for c in self.panel.get_controls_of_type(UpgradeIcon)])
        return l        

class SavedUpgradeState(UpgradeState):
    def __init__(self, scene):
        super().__init__(scene)

    def enter(self):
        self.scene.paused = True
        self.selected_targets = []
        self.extras = []
        self.panel = None
        return UIEnabledState.enter(self)

    def finish(self, target=None, cancel = False):
        for extra in self.extras:
            extra.kill()
        self.extras = []        
        if not cancel:
            self.scene.invalidate_saved_upgrade(self.pending_upgrade)
            self.scene.player_civ.register_research(self.pending_upgrade.name)
        self.scene.sm.transition(levelstates.PlayState(self.scene))

    def on_back(self):
        for extra in self.extras:
            extra.kill()        
        self.scene.sm.transition(levelstates.PlayState(self.scene))
