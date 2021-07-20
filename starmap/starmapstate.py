import game
import joystickcursor
import levelscene
import levelstates
import menuscene
import sound
import states
from button import Button
from helper import get_nearest
from loadingscene import LoadingScene
from selector import Selector
from store.storenode import StoreNodeGraphic, StoreNodePanel
from store.storescene import StoreScene
from v2 import V2

from starmap.galaxy import Galaxy

from . import starmapscene
from .galaxypanel import GalaxyPanel


class StarMapState(states.UIEnabledState):
    def __init__(self, scene):
        super().__init__(scene)
        self.joystick_overlay = None

    def enter(self):
        self.selector = None
        self.current_panel = None
        self.drag_start = None
        super().enter()

    def update(self, dt):
        if self.last_clicked_sprite:
            selection_info = self.last_clicked_sprite.get_selection_info()
            if selection_info and selection_info['type'] in ['galaxy', 'store']:
                if self.current_panel and self.current_panel.panel_for != self.last_clicked_sprite:
                    self.current_panel.kill()
                    self.current_panel = None

                if self.current_panel and self.last_clicked_sprite.needs_panel_update:
                    self.last_clicked_sprite.needs_panel_update = False
                    self.current_panel.kill()
                    self.current_panel = None                    

                if not self.current_panel:
                    if selection_info['type'] == 'galaxy':
                        self.current_panel = GalaxyPanel(self.last_clicked_sprite, self.click_launch)
                    else:
                        self.current_panel = StoreNodePanel(self.last_clicked_sprite, self.click_store)
                    sound.play("panel")
                    self.current_panel.position_nicely(self.scene)
                    self.current_panel.add_all_to_group(self.scene.ui_group)
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

        if self.scene.game.input_mode == "joystick":
            self.joystick_update(dt)
        super().update(dt)

    def click_store(self, store):
        sound.play("click1")
        self.scene.game.run_info.choose_path(*store.coords)
        self.scene.game.scene = StoreScene(self.scene.game,store)
        self.scene.game.scene.start()

    def click_launch(self, galaxy):
        sound.play("click1")
        self.scene.game.run_info.choose_path(*galaxy.coords)
        self.scene.game.scene = LoadingScene(self.scene.game,galaxy)
        self.scene.game.scene.start()

    def take_input(self, input, event):
        if hasattr(event, 'gpos'):
            event.gpos -= self.scene.scroll_panel.pos
        super().take_input(input, event)
        if not self.hover_sprite:
            if input == 'click':
                self.drag_start = event.gpos
            if input == 'mouse_drag':
                self.scene.scroll_panel.scroll(self.scene.scroll_panel.pos + event.grel)

        if input == "menu":
            self.scene.game.scene = menuscene.MenuScene(self.scene.game)
            self.scene.game.scene.start()
                
    def joy_hover_filter(self, spr):
        return isinstance(spr, Galaxy) or isinstance(spr, StoreNodeGraphic)

    def joystick_update(self, dt):
        all_sprites = []
        all_sprites.extend(
            sorted(self.scene.ui_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )        
        all_sprites.extend(
            sorted(self.scene.game_group.sprites()[::], key=lambda x:x.layer, reverse=True)
        )
        selectable_sprites = [s for s in all_sprites if s.selectable and s.visible and self.joy_hover_filter(s)]

        scrolled_pos = self.joystick_overlay.cursor_pos - self.scene.scroll_panel.pos
        nearest, d = get_nearest(scrolled_pos, selectable_sprites)
        if d < 40 ** 2:
            self.joystick_overlay.set_nearest(nearest)
        else:
            self.joystick_overlay.set_nearest(None)

        if self.current_panel and self.current_panel.panel_for != self.joystick_overlay.nearest_obj:
            self.current_panel.kill()
            self.current_panel = None
            self.last_clicked_sprite = None

        if self.joystick_overlay.cursor_pos.x < 20:
            self.scene.scroll_panel.scroll(self.scene.scroll_panel.pos + V2(300 * dt, 0))
        if self.joystick_overlay.cursor_pos.x > game.RES[0] - 20:
            self.scene.scroll_panel.scroll(self.scene.scroll_panel.pos + V2(-300 * dt, 0))
        if self.joystick_overlay.cursor_pos.y < 20:
            self.scene.scroll_panel.scroll(self.scene.scroll_panel.pos + V2(0, 300 * dt))
        if self.joystick_overlay.cursor_pos.y > game.RES[1] - 20:
            self.scene.scroll_panel.scroll(self.scene.scroll_panel.pos + V2(0, -300 * dt))

        self.joystick_overlay.cursor_pos = self.joystick_overlay.cursor_pos.rect_contain(20, 20, game.RES[0] - 40, game.RES[1] - 40)

    def set_joystick_input(self):
        if not self.joystick_overlay:
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, V2(200, 200))
            self.scene.ui_group2.add(self.joystick_overlay)
        return super().set_joystick_input()

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "confirm":
            if self.current_panel:
                self.current_panel.get_control_of_type(Button).onclick()
            else:
                if self.joystick_overlay.nearest_obj:
                    self.last_clicked_sprite = self.joystick_overlay.nearest_obj
