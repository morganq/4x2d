import levelstates
from .galaxypanel import GalaxyPanel
from selector import Selector
import levelscene
from . import starmapscene
import states

class StarMapState(states.UIEnabledState):
    def enter(self):
        self.selector = None
        self.current_panel = None
        self.drag_start = None
        super().enter()

    def update(self, dt):
        if self.last_clicked_sprite:
            selection_info = self.last_clicked_sprite.get_selection_info()
            if selection_info and selection_info['type'] == 'galaxy':
                if self.current_panel and self.current_panel.panel_for != self.last_clicked_sprite:
                    self.current_panel.kill()
                    self.current_panel = None

                if self.current_panel and self.last_clicked_sprite.needs_panel_update:
                    self.last_clicked_sprite.needs_panel_update = False
                    self.current_panel.kill()
                    self.current_panel = None                    

                if not self.current_panel:
                    self.current_panel = GalaxyPanel(self.last_clicked_sprite, self.click_launch)
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

    def click_launch(self, galaxy):
        print(galaxy)
        self.scene.game.run_info.choose_path(*galaxy.coords)
        self.scene.game.scene = levelscene.LevelScene(self.scene.game, galaxy.level, galaxy.alien, galaxy.difficulty)
        # self.scene.game.scene = starmapscene.StarMapScene(self.scene.game)
        self.scene.game.scene.start()

    def take_input(self, input, event):
        if hasattr(event, 'gpos'):
            event.gpos -= self.scene.scroll_panel.pos
        super().take_input(input, event)
        if not self.hover_sprite:
            if input == 'click':
                self.drag_start = event.gpos
            if input == 'mouse_drag':
                
                self.scene.scroll_panel.pos += event.grel
                