import pygame

import game
import rewardscene
import save
import sound
import starmap
import text
from anyupgradepanel import AnyUpgradePanel
from arrow import OrderArrow
from button import Button
from colors import *
from funnotification import FunNotification
from helppanel import HelpPanel
from orderpanel import OrderPanel
from planet.planetpanel import PlanetPanel
from rangeindicator import RangeIndicator
from resources import resource_path
from selector import Selector
from simplesprite import SimpleSprite
from states import State, UIEnabledState
from upgrade.upgradepanel import UpgradePanel
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2

class PlayState(UIEnabledState):
    def enter(self):
        UIEnabledState.enter(self)
        self.selector = None # Selection object
        self.arrow = None # Order object
        self.current_panel = None

    def exit(self):
        if self.selector:
            self.selector.kill()
        if self.arrow:
            self.arrow.kill()
        if self.current_panel:
            self.current_panel.kill()
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
        if self.last_clicked_sprite:
            selection_info = self.last_clicked_sprite.get_selection_info()
            if selection_info and selection_info['type'] == 'planet':
                if self.current_panel and self.current_panel.panel_for != self.last_clicked_sprite:
                    self.current_panel.kill()
                    self.current_panel = None


                just_update = self.last_clicked_sprite.needs_panel_update
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
        super().update(dt)

    def take_input(self, inp, event):
        if game.DEV:
            if inp == "other" and event.key == pygame.K_u:
                self.scene.sm.transition(DevAnyUpgradeState(self.scene))
                
                # name = input("updgrade name> ")
                # # Get all applicable upgrades
                # reg = re.compile(name)
                # for u in [u for u in UPGRADE_CLASSES.values() if u.alien == False and reg.match(u.name)]:
                #     self.scene.my_civ.researched_upgrade_names.add(u.name)
                #     if u.cursor == None:
                #         self.scene.my_civ.upgrades.append(u)
                #         u().apply(self.scene.my_civ)
                #         self.scene.ui_group.add(FunNotification(u.title, None))
                #     elif u.cursor == "allied_planet":
                #         planet = self.scene.get_civ_planets(self.scene.my_civ)[0]
                #         u().apply(planet)

            if inp == "other" and event.key == pygame.K_p:
                self.scene.paused = not self.scene.paused

            if inp == "other" and event.key == pygame.K_s:
                name = input("ship name> ")
                self.scene.get_civ_planets(self.scene.my_civ)[0].add_ship(name)

            if inp == "click":
                pass
                #e = explosion.Explosion(event.gpos, [PICO_WHITE, PICO_YELLOW, PICO_ORANGE, PICO_RED, PICO_RED], 0.25, 6, scale_fn="log", line_width=3)
                #self.scene.game_group.add(e)

        return super().take_input(inp, event)

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
    def __init__(self, scene, planet_from, planet_to, path=None):
        UIEnabledState.__init__(self, scene)
        self.planet_from = planet_from
        self.planet_to = planet_to
        self.path = path

    def deselect(self):
        pass

    def enter(self):
        UIEnabledState.enter(self)
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

    def exit(self):
        self.hover_filter = lambda x: True
        self.panel.kill()
        self.arrow.kill()
        self.scene.paused = False
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

class UpgradeState(UIEnabledState):
    NEARBY_RANGE = 70
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
            x.upgradeable
        ) or x == self.back_button

    def filter_my_fleets(self, x):
        return (
            x.get_selection_info() and x.get_selection_info()['type'] == 'fleet' and x.owning_civ == self.scene.my_civ
        ) or x == self.back_button        

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
        self.scene.sm.transition(PlayState(self.scene))

    def on_reroll(self):
        self.scene.my_civ.clear_offers()
        self.panel.kill()
        self.scene.game.run_info.rerolls -= 1
        resource = self.scene.my_civ.upgrades_stocked[0]
        self.panel = UpgradePanel(V2(0,0), self.scene.my_civ.offer_upgrades(resource), resource, self.on_select, self.on_reroll)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        self.panel.fade_in(speed=10)

    def setup_cursor_type(self, cursor):
        if cursor == "allied_planet":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_my_planets
            if self.panel:
                self.panel.kill()
            self.selection_info_text = text.Text("Select one of your Planets to apply upgrade", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)
        elif cursor == "allied_fleet":
            self.scene.fleet_managers['my'].generate_selectable_objects()
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-fleet-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_my_fleets
            if self.panel:
                self.panel.kill()
            self.selection_info_text = text.Text("Select one of your Fleets to apply upgrade", "big", V2(170, 150), PICO_WHITE, multiline_width=180,shadow=PICO_BLACK)
            self.scene.ui_group.add(self.selection_info_text)
        elif cursor == "point":
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-point-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = self.filter_only_ui
            if self.panel:
                self.panel.kill()
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
            if self.panel:
                self.panel.kill()
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

    def update(self, dt):
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
        self.scene.sm.transition(PlayState(self.scene))        

    def on_back(self):
        return

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
        self.scene.sm.transition(PlayState(self.scene))

    def on_back(self):
        for extra in self.extras:
            extra.kill()        
        self.scene.sm.transition(PlayState(self.scene))

class GameOverState(State):
    def enter(self):
        scores = save.SAVE_OBJ.add_highscore(self.scene.score)
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
        t = text.Text("Click to continue", "medium", V2(250, 200), PICO_WHITE, multiline_width=200)
        t.offset = (0.5,0)
        self.scene.ui_group.add(t)

        self.scene.ui_group.add(FunNotification("VICTORY!"))

        for r in self.scene.my_civ.upgrades_stocked:
            if r == "iron": self.scene.game.run_info.bonus_credits += 10
            elif r == "ice": self.scene.game.run_info.bonus_credits += 15
            elif r == "gas": self.scene.game.run_info.bonus_credits += 20

        return super().enter()

    def take_input(self, input, event):
        if input == "action" or input == "click":
            self.scene.game.scene = rewardscene.RewardScene(
                self.scene.game,
                [u.name for u in self.scene.my_civ.upgrades],
                [u for u in self.scene.my_civ.researched_upgrade_names if UPGRADE_CLASSES[u].category == 'buildings'],
            )
            self.scene.game.scene.start()
                                