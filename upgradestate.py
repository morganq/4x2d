import pygame

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
from v2 import V2


class UpgradeState(UIEnabledState):
    NEARBY_RANGE = 70
    is_basic_joystick_panel = True
    def __init__(self, scene):
        UIEnabledState.__init__(self, scene)
        self.pending_upgrade = None
        self.cursor_icon = None
        self.selection_info_text = None
        self.back_button = None
        self.current_cursor = None

    def enter(self):
        sound.play("panel")
        self.scene.paused = True
        self.scene.upgrade_button.visible = False
        resource = self.scene.my_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.my_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in(speed=10)
        self.hover_filter = self.filter_only_panel_ui
        self.selected_targets = []
        self.extras = []
        super().enter()

    def filter_my_planets(self, x):
        return (
            x.get_selection_info() and
            x.get_selection_info()['type'] == 'planet' and
            x.owning_civ == self.scene.my_civ and 
            x.upgradeable and
            x.is_buildable()
        ) or x == self.back_button

    def filter_my_fleets(self, x):
        return (
            x.get_selection_info() and x.get_selection_info()['type'] == 'fleet' and x.owning_civ == self.scene.my_civ
        ) or x == self.back_button       

    def get_joystick_cursor_controls(self):
        l = []
        l.extend([[c] for c in self.panel.get_controls_of_type(UpgradeButton)])
        l.append([self.panel.get_control_of_type(Button)])
        return l

    def exit(self):
        self.hover_filter = lambda x:True
        self.scene.paused = False
        if self.selection_info_text:
            self.selection_info_text.kill()
        if self.cursor_icon:
            self.cursor_icon.kill()
        if self.back_button:
            self.back_button.kill()
        super().exit()

    def finish(self, target=None, cancel = False):
        for extra in self.extras:
            extra.kill()
        self.extras = []        
        if not cancel:
            self.scene.my_civ.upgrades_stocked.pop(0)
            self.scene.my_civ.researched_upgrade_names.add(self.pending_upgrade.name)
            self.scene.my_civ.clear_offers()
            sound.play("upgrade2")
        if self.panel:
            self.panel.kill()
        if self.joystick_overlay:
            self.joystick_overlay.kill()
        self.scene.sm.transition(levelstates.PlayState(self.scene))

    def on_reroll(self):
        self.scene.my_civ.clear_offers()
        self.panel.kill()
        self.scene.game.run_info.rerolls -= 1
        resource = self.scene.my_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.my_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll)
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
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos)
            self.scene.ui_group.add(self.joystick_overlay)
            self.joystick_overlay.set_button_options(["[*x*] Select"])

        if self.panel:
            self.panel.kill()
        if cursor == "allied_planet":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_my_planets
            self.selection_info_text = text.Text("Select one of your Planets to apply upgrade", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)
        elif cursor == "allied_fleet":
            self.scene.fleet_managers['my'].generate_selectable_objects()
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-fleet-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_my_fleets
            self.selection_info_text = text.Text("Select one of your Fleets to apply upgrade", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)
        elif cursor == "point":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_only_ui
            self.selection_info_text = text.Text("Select a point", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)
        elif cursor == "nearby":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.range = RangeIndicator(self.selected_targets[0].pos, self.NEARBY_RANGE, PICO_LIGHTGRAY)
            self.scene.ui_group.add(self.range)
            self.extras.append(self.range)
            self.hover_filter = self.filter_only_ui
            self.selection_info_text = text.Text("Select a point nearby", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)                     

    def on_select(self, upgrade):
        if isinstance(upgrade.cursor, list):
            self.cursors = upgrade.cursor[::]
        else:
            self.cursors = [upgrade.cursor]

        self.current_cursor = self.cursors.pop(0)

        if self.current_cursor == None:
            self.pending_upgrade = upgrade
            self.scene.my_civ.upgrades.append(upgrade)
            upgrade().apply(self.scene.my_civ)
            self.scene.ui_group.add(FunNotification(self.pending_upgrade.title, None))
            self.finish()
        else:
            self.pending_upgrade = upgrade
            self.setup_cursor_type(self.current_cursor)
            self.back_button = Button(self.scene.upgrade_button.pos, "Back", "small", self.on_back)
            self.back_button.offset = (0.5, 1)
            self.scene.ui_group.add(self.back_button)            

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
        if handled:
            return
        if self.cursor_icon:
            if input in ["mouse_move", "mouse_drag"]:
                self.cursor_icon.pos = event.gpos + V2(10,10)

        if self.current_cursor:
            if input == "click" and self.hover_sprite:
                sel = self.hover_sprite.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and self.hover_sprite.owning_civ == self.scene.my_civ:
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
                if (event.gpos - self.selected_targets[0].pos).sqr_magnitude() < self.NEARBY_RANGE ** 2:
                    self.selected_targets.append(event.gpos)
                    self.next_selection_step()
                    return                

        else:
            if input == "click":
                pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
                if not pr.collidepoint(event.gpos.tuple()):
                    self.finish(cancel = True)

    def keyboard_input(self, input, event):
        super().keyboard_input(input, event)
        if self.cursor_icon:
            if input == 'action' and self.hover_sprite:
                sel = self.hover_sprite.get_selection_info()
                if sel and sel['type'] == "planet" and self.hover_sprite.owning_civ == self.scene.my_civ:
                    u = self.pending_upgrade().apply(self.hover_sprite)
                    self.finish(target=self.hover_sprite)      

    def joystick_input(self, input, event):
        if input == "back":
            if self.pending_upgrade:
                self.on_back()
            else:
                self.finish(cancel = True)

        if self.pending_upgrade is None:
            return super().joystick_input(input, event)

        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "confirm":
            spr = self.joystick_overlay.nearest_obj
            if spr:
                sel = spr.get_selection_info()
                if sel:
                    if self.current_cursor == "allied_planet" and sel['type'] == "planet" and spr.owning_civ == self.scene.my_civ:
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
                if (self.joystick_overlay.cursor_pos - self.selected_targets[0].pos).sqr_magnitude() < self.NEARBY_RANGE ** 2:
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
        if self.cursor_icon:
            self.cursor_icon.kill()
            self.cursor_icon = None

        self.cursor_type = None
        self.pending_upgrade = None
        resource = self.scene.my_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.my_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in(speed=10)
        self.hover_filter = self.filter_only_panel_ui
        self.back_button.kill()
        self.back_button = None
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
            self.scene.my_civ.researched_upgrade_names.add(self.pending_upgrade.name)
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
            self.scene.my_civ.researched_upgrade_names.add(self.pending_upgrade.name)
        self.scene.sm.transition(levelstates.PlayState(self.scene))

    def on_back(self):
        for extra in self.extras:
            extra.kill()        
        self.scene.sm.transition(levelstates.PlayState(self.scene))
