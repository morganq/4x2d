from store.storenode import StoreNodePanel
import levelstates
from .galaxypanel import GalaxyPanel
from selector import Selector
import levelscene
from . import starmapscene
from loadingscene import LoadingScene
import states
import sound
from store.storescene import StoreScene
import menuscene

class StarMapState(states.UIEnabledState):
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

        if input == "back":
            self.scene.game.scene = menuscene.MenuScene(self.scene.game)
            self.scene.game.scene.start()
                