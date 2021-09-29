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
        pass

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
        #self.scene.game.run_info.choose_path(*galaxy.coords)
        self.scene.game.run_info.next_path_segment = galaxy.coords
        self.scene.game.scene = LoadingScene(self.scene.game,galaxy)
        self.scene.game.scene.start()

    def take_input(self, input, event):
        super().take_input(input, event)

        if input == "menu":
            self.scene.game.scene = menuscene.MenuScene(self.scene.game)
            self.scene.game.scene.start()
                
    def joy_hover_filter(self, spr):
        return isinstance(spr, Galaxy) or isinstance(spr, StoreNodeGraphic)

    def joystick_update(self, dt):
        pass

    def set_joystick_input(self):
        if not self.joystick_overlay:
            self.joystick_overlay = joystickcursor.JoystickCursor(self.scene, V2(200, 200))
            self.scene.ui_group.add(self.joystick_overlay)
        return super().set_joystick_input()

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joystick_overlay.joystick_delta(event['delta'])

        if input == "confirm":
            if self.current_panel:
                try:
                    self.current_panel.press_confirm()
                except AttributeError as e:
                    print(e)
            else:
                if self.joystick_overlay.nearest_obj:
                    self.last_clicked_sprite = self.joystick_overlay.nearest_obj
