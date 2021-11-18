import datetime
import math

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
from aliens import bossmothership
from anyupgradepanel import AnyUpgradePanel
from arrow import OrderArrow
from asteroid import Asteroid
from button import Button
from colors import *
from elements import expandingtext
from funnotification import FunNotification
from helper import clamp, get_nearest
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
        if (input == "click" or input == "confirm") and self.time > self.scene.stage_name.visible_time:
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
        if self.dragging_from_sprite and self.dragging_from_sprite.get_selection_info() and self.dragging_from_sprite.owning_civ == self.scene.player_civ:
            if self.hover_sprite and self.dragging_from_sprite != self.hover_sprite:
                target_selection = self.hover_sprite.get_selection_info()
                if target_selection:
                    if target_selection['type'] in ['planet', 'boss']:
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
            if self.hover_sprite.owning_civ == self.scene.player_civ:
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
            if selection_info and selection_info['type'] == 'planet' and self.dragging_from_sprite.owning_civ == self.scene.player_civ:
                if not self.arrow:
                    self.arrow = OrderArrow()
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
            print("rightclick")
            self.scene.fleet_managers['my'].point_recall(event.gpos)

        if inp == "mouse_move":
            self.mouse_pos = event.gpos
        if inp == "mouse_drag":
            self.mouse_pos = event.gpos

        return super().take_input(inp, event)

    def default_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet) or isinstance(x, upgrade.upgradeicon.UpgradeIcon)

    def target_joy_hover_filter(self, x):
        return isinstance(x, planet.planet.Planet) or isinstance(x, Asteroid) or isinstance(x, bossmothership.BossMothership)

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
                if nearest.owning_civ == self.scene.player_civ:
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
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, self.scene.game.last_joystick_pos[0])
            self.scene.ui_group.add(self.joystick_overlay)
        return super().set_joystick_input()

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if game.DEV and input == "cheat1":
            self.scene.sm.transition(VictoryState(self.scene))

        if input == "special" and len(self.scene.player_civ.upgrades_stocked) > 0:
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
                        if target_selection['type'] in ['planet', 'boss', 'asteroid']:
                            self.scene.sm.transition(OrderShipsState(self.scene, self.joy_arrow_from, spr))
                            spr.on_mouse_exit(V2(0,0))

        if input == "action":
            if self.joy_controls_state == "default":
                spr = self.joystick_overlay.nearest_obj
                if spr and spr.owning_civ == self.scene.player_civ:
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
            if sel and sel['type'] == 'planet' and self.key_picked_sprite.owning_civ == self.scene.player_civ:
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
        self.scene.update_run_stats()
        self.scene.game.game_speed_input = 0
        #self.scene.game_group.empty()

        self.scene.ui_group.empty()
        self.scene.pause_sprite.darken()
        self.scene.ui_group.add(self.scene.pause_sprite)

        ts = expandingtext.ExpandingText(V2(self.scene.game.game_resolution.x/2 + 2, 100 + 2), "DEFEAT", color=PICO_WHITE)
        ts.offset = (0.5, 0)
        ts.layer = 9
        self.scene.ui_group.add(ts)

        t = expandingtext.ExpandingText(V2(self.scene.game.game_resolution.x/2, 100), "DEFEAT", color=PICO_RED)
        t.offset = (0.5, 0)
        t.layer = 10
        self.scene.ui_group.add(t)
        self.time = 0

    def paused_update(self, dt):
        self.time += dt
        if self.time > 2:
            self.scene.sm.transition(HighScoreState(self.scene))
        return super().paused_update(dt)
                

class VictoryState(State):
    def enter(self):
        self.scene.ui_group.empty()
        self.scene.game.game_speed_input = 0

        sn = StageName(V2(0,100), self.scene.stage_num, "Victory!", "We've taken full control of this sector!")
        sn.time = 1.75
        self.scene.ui_group.add(sn)

        self.scene.game.run_info.bonus_credits += 30
        for r in self.scene.player_civ.upgrades_stocked:
            if r == "iron": self.scene.game.run_info.bonus_credits += 5
            elif r == "ice": self.scene.game.run_info.bonus_credits += 10
            elif r == "gas": self.scene.game.run_info.bonus_credits += 15
        self.scene.game.run_info.bonus_credits = min(self.scene.game.run_info.bonus_credits, 90)

        self.scene.update_run_stats()
        self.scene.game.run_info.sectors_cleared += 1

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
            [u.name for u in self.scene.player_civ.upgrades],
            [u for u in self.scene.player_civ.researched_upgrade_names if UPGRADE_CLASSES[u].category == 'buildings'],
        )
        self.scene.game.scene.start()

    def take_input(self, input, event):
        if self.time > 2 and (input == "action" or input == "click" or input == "confirm"):
            self.end()

class BeatGameState(State):
    def enter(self):
        super().enter()

        self.scene.game.game_speed_input = 0

        self.scene.update_run_stats()
        self.scene.game.run_info.victory = True
        self.scene.game.run_info.sectors_cleared += 1

        self.scene.ui_group.empty()
        self.scene.pause_sprite.darken()
        self.scene.ui_group.add(self.scene.pause_sprite)

        ts = expandingtext.ExpandingText(V2(self.scene.game.game_resolution.x/2 + 2, 100 + 2), "VICTORY", color=PICO_RED)
        ts.offset = (0.5, 0)
        ts.layer = 9
        self.scene.ui_group.add(ts)

        t = expandingtext.ExpandingText(V2(self.scene.game.game_resolution.x/2, 100), "VICTORY")
        t.offset = (0.5, 0)
        t.layer = 10
        self.scene.ui_group.add(t)
        self.time = 0

    def paused_update(self, dt):
        self.time += dt
        if self.time > 2:
            self.scene.sm.transition(HighScoreState(self.scene))
        return super().paused_update(dt)

class HighScoreState(State):
    def enter(self):
        super().enter()
        self.score_parts = []
        self.time = 0

        # Scoring
        num_sectors = self.scene.game.run_info.sectors_cleared
        minutes, seconds = divmod(int(self.scene.game.run_info.time_taken), 60)
        time_formatted = "%d:%02d" % (minutes, seconds)

        victory_bonus = 10_000 if self.scene.game.run_info.victory else 0
        sectors_bonus = 2000 * num_sectors
        time_per = self.scene.game.run_info.time_taken / max(num_sectors,1)
        # 0 second avg = 10k
        # 120 second avg = 5k
        # 360 sec = 2.5k
        time_bonus = int(1_200_000 / (time_per + 120))

        # 0 lost = 10k
        # 10 lost = 5k
        # 30 lost = 2.5k
        ships_bonus = int(100_000 / (self.scene.game.run_info.ships_lost + 10))
        if not self.scene.game.run_info.victory:
            ships_bonus = 0

        self.score = victory_bonus + sectors_bonus + time_bonus + ships_bonus
        scores = save.SAVE_OBJ.add_highscore(self.score)
        save.SAVE_OBJ.save()

        self.add_score_part("Cleared %d hostile sectors:" % num_sectors, sectors_bonus)
        self.add_score_part("Victory Bonus:", victory_bonus)
        self.add_score_part("Time Bonus (%s):" % time_formatted, time_bonus)
        if self.scene.game.run_info.victory:
            self.add_score_part("Safety Bonus (lost %d ships):" % self.scene.game.run_info.ships_lost, ships_bonus)
        else:
            self.add_score_part("Safety Bonus (lost %d ships):" % self.scene.game.run_info.ships_lost, "0 (Defeat)")
        self.add_score_part("Total:", self.score)


        self.highscores = []
        self.add_scores()

        self.scene.game.end_run()

    def add_scores(self):
        picked_one = False
        x = self.scene.game.game_resolution.x / 2 - 120
        y = self.scene.game.game_resolution.y / 2 - 40
        label = text.Text("Top Scores", "big", V2(x - 60, y), PICO_WHITE, multiline_width=200)
        label.layer = 10
        label.visible = False
        self.highscores.append(label)
        self.scene.ui_group.add(label)
        places = ['1st', '2nd', '3rd', '4th', '5th', '6th', '7th', '8th', '9th', '10th']
        for i, score in enumerate(save.SAVE_OBJ.get_highscores()):
            color = PICO_WHITE
            if score == int(self.score) and not picked_one:
                color = PICO_YELLOW
                picked_one = True
            t1 = text.Text(places[i], "small", V2(x - 40, i * 18 + y + 20), color)
            t1.offset = (1, 0)
            t1.layer = 10
            t1._recalc_rect()
            t2 = text.Text("%d" % score, "big", V2(x, i * 18 + y + 20), color)
            t2.layer = 10
            self.scene.ui_group.add(t1)
            self.scene.ui_group.add(t2)    
            t1.visible = False
            t2.visible = False    
            self.highscores.extend([t1,t2])

    def add_score_part(self, name, score):
        x = self.scene.game.game_resolution.x / 2 - 90
        y = (len(self.score_parts) // 2) * 24 + self.scene.game.game_resolution.y / 2 - 40
        tname = text.Text(name, "small", V2(x,y), PICO_WHITE, multiline_width=200, shadow=PICO_BLACK)
        tname.layer = 10
        self.scene.ui_group.add(tname)
        self.score_parts.append(tname)
        tname.visible = False
        tname.initial_x = tname.x

        tscore = text.Text(str(score), "small", V2(x + 160,y), PICO_YELLOW, multiline_width=120, shadow=PICO_BLACK)
        tscore.layer = 10
        self.scene.ui_group.add(tscore)        
        self.score_parts.append(tscore)
        tscore.visible = False
        tscore.initial_x = tscore.x

    def paused_update(self, dt):
        self.time += dt
        for i,part in enumerate(self.score_parts):
            part.visible = self.time > i / 3
            xt = clamp(self.time - 4, 0, 1)
            xo = (math.cos(xt * 3.14159) * -0.5 + 0.5) * 110
            part.x = part.initial_x + xo

        for i,part in enumerate(self.highscores):
            part.visible = self.time > (i / 10) + 5.25

        return super().paused_update(dt)

    def take_input(self, input, event):
        if input in ['confirm', 'back', 'click'] and self.time > 7:
            self.scene.game.set_scene("menu")
        return super().take_input(input, event)

class PauseState(UIEnabledState):
    is_basic_joystick_panel = True
    def enter(self):
        self.scene.paused = True
        self.panel = pausepanel.PausePanel(V2(0,0), None, self.on_resume, self.on_quit)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in()
        self.panel.add_all_to_group(self.scene.ui_group)
        self.scene.game.fps_limited_pause = True

        return super().enter()

    def get_joystick_cursor_controls(self):
        return [[b] for b in self.panel.get_controls_of_type(Button)]

    def on_resume(self):
        self.scene.sm.transition(PlayState(self.scene))

    def on_quit(self):
        self.scene.game.fps_limited_pause = False
        if not self.scene.is_tutorial:
            self.scene.game.end_run()
        self.scene.game.set_scene("menu")

    def exit(self):
        self.scene.paused = False
        self.scene.game.fps_limited_pause = False
        self.panel.kill()
        return super().exit()
