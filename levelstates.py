import pygame

import game
import joystickcursor
import menuscene
import pausepanel
import planet
import rewardscene
import save
import sound
import starmap
import text
import upgrade
import upgradestate
from anyupgradepanel import AnyUpgradePanel
from arrow import OrderArrow
from asteroid import Asteroid
from button import Button
from colors import *
from funnotification import FunNotification
from helper import get_nearest
from helppanel import HelpPanel
from orderpanel import OrderPanel
from planet.planetpanel import PlanetPanel
from rangeindicator import RangeIndicator
from resources import resource_path
from selector import Selector
from simplesprite import SimpleSprite
from stagename import StageName
from states import State, UIEnabledState
from upgrade.upgradebutton import UpgradeButton
from upgrade.upgradepanel import UpgradePanel
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2


class BeginState(State):
    def __init__(self, scene):
        self.time = 0
        super().__init__(scene)

    def update(self, dt):
        self.time += dt
        self.scene.paused = True
        return super().update(dt)

    def paused_update(self, dt):
        self.time += dt
        if not self.scene.stage_name.alive():
            self.scene.sm.transition(PlayState(self.scene))
        return super().update(dt)

    def exit(self):
        self.scene.paused = False
        return super().exit()

    def take_input(self, input, event):
        if input == "click" and self.time > self.scene.stage_name.visible_time:
            self.scene.stage_name.time = max(self.scene.stage_name.time, self.scene.stage_name.close_time)
            #self.scene.stage_name.kill()
            #self.scene.sm.transition(PlayState(self.scene))

        return super().take_input(input, event)

class CinematicState(State):
    def enter(self):
        self.scene.cinematic = True
        self.scene.game.game_speed_input = 0
        #self.hidden_ui = []
        #for spr in self.scene.ui_group.sprites():
        #    if spr.visible:
        #        self.hidden_ui.append(spr)
        #        spr.visible = False
        return super().enter()

    def exit(self):
        self.scene.cinematic = False
        #for spr in self.hidden_ui:
        #    spr.visible = True
        return super().exit()

class PlayState(UIEnabledState):
    def __init__(self, scene):
        super().__init__(scene)
        self.joystick_overlay = None

    def enter(self):
        UIEnabledState.enter(self)
        self.selector = None # Selection object
        self.arrow = None # Order object
        self.current_panel = None
        self.mouse_pos = V2(0,0)
        self.joy_controls_state = "default"
        self.joy_hover_filter = self.default_joy_hover_filter
        self.joy_arrow_from = None
        self.options_text = text.Text("", "small", V2(0,0), PICO_PINK, multiline_width=200, shadow=PICO_BLACK, center=False)
        self.scene.ui_group.add(self.options_text)

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
        if self.dragging_from_sprite and self.dragging_from_sprite.get_selection_info() and self.dragging_from_sprite.owning_civ == self.scene.my_civ:
            if self.hover_sprite and self.dragging_from_sprite != self.hover_sprite:
                target_selection = self.hover_sprite.get_selection_info()
                if target_selection:
                    if target_selection['type'] == 'planet':
                        self.scene.sm.transition(OrderShipsState(self.scene, self.dragging_from_sprite, self.hover_sprite))
                        self.hover_sprite.on_mouse_exit(V2(0,0))
                        self.hover_sprite = None
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)

                    if target_selection['type'] == 'asteroid':
                        self.scene.sm.transition(OrderShipsState(self.scene, self.dragging_from_sprite, self.hover_sprite))
                        self.hover_sprite.on_mouse_exit(V2(0,0))
                        self.hover_sprite = None
                        pygame.mouse.set_system_cursor(pygame.SYSTEM_CURSOR_ARROW)                        

    def update(self, dt):
        if self.scene.game.input_mode == "joystick":
            self.joystick_update(dt)
        else:
            self.mouse_update(dt)

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
            if self.hover_sprite.owning_civ == self.scene.my_civ:
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
                    self.current_panel = PlanetPanel(self.last_clicked_sprite)
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
                    self.selector = Selector(self.last_clicked_sprite)
                    self.scene.ui_group.add(self.selector)
        else:
            if self.selector:
                self.selector.visible = 0

        if self.dragging_from_sprite:
            selection_info = self.dragging_from_sprite.get_selection_info()
            if selection_info and selection_info['type'] == 'planet' and self.dragging_from_sprite.owning_civ == self.scene.my_civ:
                if not self.arrow:
                    self.arrow = OrderArrow()
                    self.scene.ui_group.add(self.arrow)
                dragging_to_sprite = None
                if self.hover_sprite:
                    dragging_to_sprite = self.hover_sprite
                    sel = dragging_to_sprite.get_selection_info()
                    if not sel or sel['type'] not in ['planet', 'asteroid']:
                        dragging_to_sprite = None
                self.arrow.setup(self.dragging_from_sprite, self.dragging_to, dragging_to_sprite)
                if self.arrow.visible:
                    self.deselect()
        else:
            if self.arrow:
                self.arrow.visible = False    

        self.scene.fleet_managers['my'].update_fleet_markers(self.mouse_pos)
        if self.scene.fleet_managers['my'].fleet_markers:
            options = "[*right*] Recall Ships"

        if self.arrow and self.arrow.visible:
            options = ""
            
        self.options_text.set_text(options)
        super().update(dt)

    def take_input(self, inp, event):
        if game.DEV:
            if inp == "other" and event.key == pygame.K_u:
                self.scene.sm.transition(upgradestate.DevAnyUpgradeState(self.scene))

        if inp == "menu":
            self.scene.sm.transition(PauseState(self.scene))

        if inp == "rightclick":
            self.scene.fleet_managers['my'].point_recall(event.gpos)

        if inp == "mouse_move":
            self.mouse_pos = event.gpos
        if inp == "mouse_drag":
            self.mouse_pos = event.gpos

        return super().take_input(inp, event)

    def default_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet) or isinstance(x, upgrade.upgradeicon.UpgradeIcon)

    def target_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet) or isinstance(x, Asteroid)

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
            self.scene.fleet_managers['my'].update_fleet_markers(self.joystick_overlay.cursor_pos)

        nearest, d = get_nearest(self.joystick_overlay.cursor_pos, selectable_sprites)
        if d < 40 ** 2:
            self.joystick_overlay.set_nearest(nearest)
        else:
            self.joystick_overlay.set_nearest(None)
            nearest = None

        if self.joy_controls_state == "default":
            if isinstance(nearest, planet.planet.Planet):
                if nearest.owning_civ == self.scene.my_civ:
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

    def set_joystick_input(self):
        if not self.joystick_overlay:
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos)
            self.scene.ui_group.add(self.joystick_overlay)
        return super().set_joystick_input()

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if game.DEV and input == "cheat1":
            self.scene.sm.transition(VictoryState(self.scene))

        if input == "special" and len(self.scene.my_civ.upgrades_stocked) > 0:
            self.scene.on_click_upgrade()

        if input == "confirm":
            if self.joy_controls_state == "default":
                spr = self.joystick_overlay.nearest_obj
                if spr:
                    # Check if we clicked a stored upgrade
                    if isinstance(spr, upgrade.upgradeicon.UpgradeIcon):
                        spr.on_mouse_down(spr.pos)

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
                            self.current_panel = PlanetPanel(spr)
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
                            self.selector = Selector(spr)
                            self.scene.ui_group.add(self.selector)

            elif self.joy_controls_state == "arrow":
                spr = self.joystick_overlay.nearest_obj
                if spr:
                    target_selection = spr.get_selection_info()
                    if spr != self.joy_arrow_from and target_selection:
                        if target_selection['type'] == 'planet':
                            self.scene.sm.transition(OrderShipsState(self.scene, self.joy_arrow_from, spr))
                            spr.on_mouse_exit(V2(0,0))

                        if target_selection['type'] == 'asteroid':
                            self.scene.sm.transition(OrderShipsState(self.scene, self.joy_arrow_from, spr))
                            spr.on_mouse_exit(V2(0,0))

        if input == "action":
            if self.joy_controls_state == "default":
                spr = self.joystick_overlay.nearest_obj
                if spr and spr.owning_civ == self.scene.my_civ:
                    self.joy_controls_state = "arrow"
                    self.arrow = OrderArrow()
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
                self.scene.fleet_managers['my'].point_recall(self.joystick_overlay.cursor_pos)

    def keyboard_input(self, input, event):
        if input == 'other' and event.key == pygame.K_RETURN:
            if self.scene.upgrade_button.visible:
                self.scene.upgrade_button.on_mouse_down(V2(0,0))

        if self.dragging_from_sprite:
            sel = self.key_picked_sprite.get_selection_info()
            if sel and sel['type'] == 'planet' and self.key_picked_sprite != self.dragging_from_sprite:
                if input == 'action':            
                    self.release_drag()
        else:
            sel = self.key_picked_sprite.get_selection_info()
            if sel and sel['type'] == 'planet' and self.key_picked_sprite.owning_civ == self.scene.my_civ:
                if input == 'action':
                    self.dragging_from_sprite = self.key_picked_sprite
                    return
        return super().keyboard_input(input, event)


class HelpState(UIEnabledState):
    def __init__(self, scene):
        UIEnabledState.__init__(self, scene)

    def enter(self):
        UIEnabledState.enter(self)
        self.panel = HelpPanel(V2(0,0))
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.pos = V2(game.RES[0] /2 - self.panel.width / 2, game.RES[1] / 2 - self.panel.height / 2)
        self.panel._reposition_children()
        self.panel.fade_in()
        self.scene.paused = True
        

    def exit(self):
        self.panel.kill()
        self.scene.paused = False
        super().exit()

    def mouse_input(self, input, event):
        if input == "click":
            pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
            if not pr.collidepoint(event.gpos.tuple()):
                self.scene.sm.transition(PlayState(self.scene))
        return super().mouse_input(input, event)        


class OrderShipsState(UIEnabledState):
    is_basic_joystick_panel = True    
    def __init__(self, scene, planet_from, planet_to, path=None):
        UIEnabledState.__init__(self, scene)
        self.planet_from = planet_from
        self.planet_to = planet_to
        self.path = path
        self.joystick_overlay = None

    def deselect(self):
        pass

    def enter(self):
        self.scene.paused = True
        self.hover_filter = self.filter_only_panel_ui
        self.panel = OrderPanel(V2(0,0), self.planet_from, self.planet_to, self.on_order)
        self.panel.position_nicely(self.scene)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.fade_in()
        self.arrow = OrderArrow()
        self.scene.ui_group.add(self.arrow)
        self.arrow.setup(self.planet_from, None, self.planet_to)
        sound.play("attackpanel")
        UIEnabledState.enter(self)

    def exit(self):
        self.hover_filter = lambda x: True
        self.panel.kill()
        self.arrow.kill()
        self.scene.paused = False
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
        self.scene.sm.transition(PlayState(self.scene))

    def mouse_input(self, input, event):
        if input == "click":
            pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
            if not pr.collidepoint(event.gpos.tuple()):
                self.scene.sm.transition(PlayState(self.scene))
        return super().mouse_input(input, event)

    def joystick_input(self, input, event):
        if input == "back":
            self.scene.sm.transition(PlayState(self.scene))

        if input == "confirm":
            self.panel.on_launch_click()
        return super().joystick_input(input, event)

    def get_joystick_cursor_controls(self):
        controls = list(self.panel.sliders.values())
        return [[c] for c in controls]



class GameOverState(State):
    def enter(self):
        print("score", "resource", self.scene.score)
        self.scene.game.run_info.score += int(self.scene.score)
        scores = save.SAVE_OBJ.add_highscore(self.scene.game.run_info.score)
        self.scene.game_group.empty()
        self.scene.ui_group.empty()
        save.SAVE_OBJ.save()
        picked_one = False
        self.scene.ui_group.add(text.Text("- High Scores -", "big", V2(170, 60), PICO_BLUE, multiline_width=200))
        places = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
        for i, score in enumerate(save.SAVE_OBJ.get_highscores()):
            color = PICO_WHITE
            if score == int(self.scene.score) and not picked_one:
                color = PICO_BLUE
                picked_one = True
            t1 = text.Text(places[i], "big", V2(240, i * 18 + 90), color)
            t1.offset = (1, 0)
            t1._recalc_rect()
            t2 = text.Text("%d" % score, "big", V2(250, i * 18 + 90), color)
            self.scene.ui_group.add(t1)
            self.scene.ui_group.add(t2)

        self.scene.game.save.set_run_state(None)

        return super().enter()

    def take_input(self, input, event):
        if input == "action" or input == "click":
            self.scene.game.set_scene("menu")
                

class VictoryState(State):
    def enter(self):
        self.scene.ui_group.empty()

        sn = StageName(V2(0,100), self.scene.stage_num, "Victory!", "We've taken full control of this sector!")
        sn.time = 1.75
        self.scene.ui_group.add(sn)

        self.scene.game.run_info.bonus_credits += 30
        for r in self.scene.my_civ.upgrades_stocked:
            if r == "iron": self.scene.game.run_info.bonus_credits += 5
            elif r == "ice": self.scene.game.run_info.bonus_credits += 10
            elif r == "gas": self.scene.game.run_info.bonus_credits += 15
        self.scene.game.run_info.bonus_credits = min(self.scene.game.run_info.bonus_credits, 90)

        speed_bonus = int((1000000 / (self.scene.time + 120)))
        print("score", "resource", self.scene.score, "speed", speed_bonus)
        self.scene.game.run_info.score += int(self.scene.score) + speed_bonus

        self.scene.game.run_info.choose_path(*self.scene.game.run_info.next_path_segment)
        self.time = 0
        self.scene.paused = True

        return super().enter()

    def paused_update(self, dt):
        self.time += dt
        if self.time > 6.5:
            self.end()
        return super().paused_update(dt)

    def end(self):
        self.scene.game.scene = rewardscene.RewardScene(
            self.scene.game,
            [u.name for u in self.scene.my_civ.upgrades],
            [u for u in self.scene.my_civ.researched_upgrade_names if UPGRADE_CLASSES[u].category == 'buildings'],
        )
        self.scene.game.scene.start()

    def take_input(self, input, event):
        if self.time > 2 and (input == "action" or input == "click" or input == "confirm"):
            self.end()

                                

class PauseState(UIEnabledState):
    is_basic_joystick_panel = True
    def enter(self):
        self.scene.paused = True
        self.panel = pausepanel.PausePanel(V2(0,0), None, self.on_resume, self.on_quit)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in()
        self.panel.add_all_to_group(self.scene.ui_group)

        return super().enter()

    def get_joystick_cursor_controls(self):
        return [[b] for b in self.panel.get_controls_of_type(Button)]

    def on_resume(self):
        self.scene.sm.transition(PlayState(self.scene))

    def on_quit(self):
        self.scene.game.scene = menuscene.MenuScene(self.scene.game)
        self.scene.game.scene.start()

    def exit(self):
        self.scene.paused = False
        self.panel.kill()
        return super().exit()
