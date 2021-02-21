from simplesprite import SimpleSprite
from states import State
import framesprite
import game
import text
import csv
import math
import pygame
import sound
from resources import resource_path
from funnotification import FunNotification
from planet.planetpanel import PlanetPanel
from orderpanel import OrderPanel
from selector import Selector
from arrow import OrderArrow
from upgrade.upgradepanel import UpgradePanel
from v2 import V2

class UIEnabledState(State):
    def enter(self):
        self.hover_sprite = None # Mouse is over this one
        self.clicking_sprite = None # Currently mouse-down-ing this one
        self.last_clicked_sprite = None # Last clicked, clears when clicking on nothing
        self.dragging_from_sprite = None # When dragging, this is the sprite dragging FROM
        self.dragging_to = None # When dragging, this is the position dragging TO
        self.hover_filter = lambda x: True

    def deselect(self):
        pass

    def release_drag(self):
        pass

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

    def deselect(self):
        self.last_clicked_sprite = None
        if self.current_panel:
            self.current_panel.kill()
            self.current_panel = None

    def release_drag(self):
        if self.hover_sprite and self.dragging_from_sprite != self.hover_sprite:
            target_selection = self.hover_sprite.get_selection_info()
            if target_selection['type'] == 'planet' and self.dragging_from_sprite.owning_civ == self.scene.my_civ:
                self.scene.sm.transition(OrderShipsState(self.scene, self.dragging_from_sprite, self.hover_sprite))

    def update(self, dt):
        if self.last_clicked_sprite:
            selection_info = self.last_clicked_sprite.get_selection_info()
            if selection_info:
                if self.current_panel and self.current_panel.panel_for != self.last_clicked_sprite:
                    self.current_panel.kill()
                    self.current_panel = None

                if not self.current_panel:
                    self.current_panel = PlanetPanel(self.last_clicked_sprite)
                    self.current_panel.position_nicely(self.scene)
                    self.current_panel.add_all_to_group(self.scene.ui_group)

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
                self.arrow.setup(self.dragging_from_sprite, self.dragging_to, dragging_to_sprite)
                if self.arrow.visible:
                    self.deselect()
        else:
            if self.arrow:
                self.arrow.visible = False        


class OrderShipsState(UIEnabledState):
    def __init__(self, scene, planet_from, planet_to):
        UIEnabledState.__init__(self, scene)
        self.planet_from = planet_from
        self.planet_to = planet_to

    def deselect(self):
        pass

    def enter(self):
        UIEnabledState.enter(self)
        self.panel = OrderPanel(V2(0,0), self.planet_from, self.planet_to, self.on_order)
        self.panel.position_nicely(self.scene)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.arrow = OrderArrow()
        self.scene.ui_group.add(self.arrow)
        self.arrow.setup(self.planet_from, None, self.planet_to)

    def exit(self):
        self.panel.kill()
        self.arrow.kill()

    def on_order(self, values):
        for ship,num in values.items():
            if ship == "colonist":
                self.planet_from.population -= num
                self.planet_from.emit_ships_queue.append((ship, {"to":self.planet_to, "num":num}))
            else:
                self.planet_from.ships[ship] -= num
                for i in range(num):
                    self.planet_from.emit_ships_queue.append((ship, {"to":self.planet_to}))
        self.scene.sm.transition(PlayState(self.scene))

    def take_input(self, input, event):
        if input == "click":
            pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
            if not pr.collidepoint(event.gpos.tuple()):
                self.scene.sm.transition(PlayState(self.scene))
        return super().take_input(input, event)


class UpgradeState(UIEnabledState):
    def __init__(self, scene):
        UIEnabledState.__init__(self, scene)
        self.pending_upgrade = None
        self.cursor_type = None
        self.cursor_icon = None

    def enter(self):
        self.scene.paused = True
        self.panel = UpgradePanel(V2(0,0), self.scene.my_civ.upgrades[0], self.on_select)
        self.panel.add_all_to_group(self.scene.ui_group)
        self.panel.position_nicely(self.scene)
        super().enter()

    def exit(self):
        self.scene.paused = False
        if self.cursor_icon:
            self.cursor_icon.kill()

    def finish(self, target=None, cancel = False):
        if not cancel:
            self.scene.ui_group.add(FunNotification(self.pending_upgrade.title, target))
            self.scene.my_civ.upgrades.pop(0)
        if self.panel:
            self.panel.kill()
        self.scene.sm.transition(PlayState(self.scene))

    def on_select(self, upgrade):
        if upgrade.cursor == None:
            self.pending_upgrade = upgrade
            self.scene.my_civ.civ_upgrades.append(upgrade.name)
            upgrade().apply(self.scene.my_civ)
            self.finish()
        else:
            self.pending_upgrade = upgrade
            self.cursor_type = upgrade.cursor
            self.cursor_icon = SimpleSprite(V2(0,0), "assets/i-planet-cursor.png")
            self.cursor_icon.offset = (0.5, 0.5)
            self.cursor_icon._recalc_rect()
            self.scene.ui_group.add(self.cursor_icon)
            self.hover_filter = lambda x:(x.get_selection_info() and x.get_selection_info()['type'] == 'planet' and x.owning_civ == self.scene.my_civ)
            self.panel.kill()

    def take_input(self, input, event):
        super().take_input(input, event)
        if self.cursor_icon:
            if input in ["mouse_move", "mouse_drag"]:
                self.cursor_icon.pos = event.gpos + V2(10,10)

            if input == "click" and self.hover_sprite:
                sel = self.hover_sprite.get_selection_info()
                if sel and sel['type'] == "planet" and self.hover_sprite.owning_civ == self.scene.my_civ:
                    self.hover_sprite.planet_upgrades.append(self.pending_upgrade.name)
                    u = self.pending_upgrade().apply(self.hover_sprite)
                    self.finish(target=self.hover_sprite)
        else:
            if input == "click":
                pr = pygame.Rect(self.panel.x, self.panel.y, self.panel.width, self.panel.height)
                if not pr.collidepoint(event.gpos.tuple()):
                    self.finish(cancel = True)