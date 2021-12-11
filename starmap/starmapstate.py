import game
import joyresolver
import joystickcursor
import levelscene
import levelstates
import menuscene
import rewardscene
import sound
import states
import text
from button import Button
from colors import *
from elements import digitalpointer, typewriter
from helper import clamp, get_nearest
from loadingscene import LoadingScene
from store import storepanel
from store.storenode import StoreNodeGraphic, StoreNodePanel
from store.storescene import StoreScene
from v2 import V2

from starmap.galaxy import Galaxy

from . import starmapscene
from .galaxypanel import GalaxyPanel


class StarMapState(states.UIEnabledState):
    def __init__(self, scene):
        super().__init__(scene)
        self.joy = joyresolver.JoyResolver(self.on_joy_direction_press)

    def enter(self):
        self.pointer = digitalpointer.DigitalPointer(V2(0,0))
        self.pointer.layer = -1
        self.selected_pointer = None
        self.scene.ui_group.add(self.pointer)
        self.current_panel = None
        self.drag_start = None
        self.display_objs = []
        self.current_node = None
        self.select_node(None)
        self.joy_controls_order = []
        self.joy_node_index = 0
        self.joy_current_confirm_button = None
        
        pickable_nodes = [n for n in self.scene.nodes if n.is_pickable()]
        if game.DEV:
            pickable_nodes = [n for n in self.scene.nodes]
        pickable_nodes.sort(key=lambda x:x.y)
        for node in pickable_nodes:
            node.on("mouse_down", self.node_click)
            node.on("mouse_enter", self.node_hover)
            node.on("mouse_exit", self.node_unhover)
            self.joy_controls_order.append(node)
        super().enter()

    def node_hover(self, obj, pos):
        if self.selected_pointer and self.selected_pointer.target == obj:
            return
        if self.selected_pointer and self.selected_pointer.target != obj:
            self.pointer = digitalpointer.DigitalPointer(V2(0,0))
            self.pointer.layer = -1
            self.scene.ui_group.add(self.pointer)
        self.pointer.set_hover(obj, radius=11, center=obj.pos + V2(1,-1))

    def node_unhover(self, obj, pos):
        if self.pointer.target == obj and self.pointer.mode == "hover":
            self.pointer.set_hidden()

    def node_click(self, obj, pos):
        if self.selected_pointer and self.selected_pointer.target == obj:
            return        
        if self.selected_pointer and obj != self.selected_pointer.target:
            self.selected_pointer.kill()
            self.selected_pointer = None
        self.pointer.set_active(obj, radius=11, center=obj.pos + V2(1,-1))
        self.selected_pointer = self.pointer
        self.select_node(obj)

    def click_store(self):
        sound.play("click1")
        self.scene.game.run_info.choose_path(*self.current_node.node_pos)
        #self.scene.game.scene = StoreScene(self.scene.game, self.current_node.get_node())
        #self.scene.game.scene.start()
        self.scene.sm.transition(StoreNodeState(self.current_node.get_node(), self.scene))

    def click_launch(self):
        sound.play("click1")
        #self.scene.game.run_info.choose_path(*galaxy.coords)
        self.scene.game.run_info.next_path_segment = self.current_node.node_pos
        self.scene.game.scene = LoadingScene(self.scene.game)
        self.scene.game.scene.start()

    def take_input(self, input, event):
        super().take_input(input, event)
        if input == "menu" or input == "back":
            self.scene.game.set_scene("menu")
                
    def on_joy_direction_press(self, direction):
        node = self.joy_controls_order[self.joy_node_index]
        node.on_mouse_exit(V2(0,0))            
        if direction == 'up':        
            self.joy_node_index = clamp(self.joy_node_index - 1, 0, len(self.joy_controls_order)-1)
            node = self.joy_controls_order[self.joy_node_index]
        if direction == 'down':
            self.joy_node_index = clamp(self.joy_node_index + 1, 0, len(self.joy_controls_order)-1)
            node = self.joy_controls_order[self.joy_node_index]
        node.on_mouse_enter(V2(0,0))
        node.on_mouse_down(V2(0,0))

    def joystick_input(self, input, event):
        if input == "joymotion":
            self.joy.take_input(input, event)

        if input == "confirm":
            if self.joy_current_confirm_button:
                self.joy_current_confirm_button.onclick()

    def select_node(self, node_sprite):
        for obj in self.display_objs:
            obj.kill()
        self.joy_current_confirm_button = None
        self.current_node = node_sprite
        if not node_sprite:
            self.create_nodeless_display()
        elif node_sprite.get_node()['node_type'] == 'galaxy':
            self.create_encounter_display(node_sprite.get_node())
        elif node_sprite.get_node()['node_type'] == 'store':
            self.create_shop_display(node_sprite.get_node())


    def create_nodeless_display(self):
        res = self.scene.game.game_resolution
        t = typewriter.Typewriter("^ Pick your next jump ^", "big", V2(res.x / 2, self.scene.background.center_y + 60), PICO_DARKGRAY, multiline_width=500)
        t.offset = (0.5, 0.5)
        self.scene.ui_group.add(t)
        self.display_objs = [t]

    def create_encounter_display(self, node):
        self.display_objs = []
        res = self.scene.game.game_resolution
        t1 = typewriter.Typewriter("Sector %d - [!Hostile]" % node['sector'], "big", V2(60, self.scene.background.center_y + 55), PICO_WHITE, multiline_width=500)
        self.scene.ui_group.add(t1)
        self.display_objs.append(t1)

        t2 = typewriter.Typewriter("Enemy: ???", "small", V2(60, self.scene.background.center_y + 75), PICO_WHITE, multiline_width=500)
        self.scene.ui_group.add(t2) 
        self.display_objs.append(t2)

        if node['rewards']:
            rew = rewardscene.REWARDS[node['rewards'][0]]['title']
            t3 = typewriter.Typewriter("Reward: %s" % rew, "small", V2(60, self.scene.background.center_y + 88), PICO_WHITE, multiline_width=500)
            self.scene.ui_group.add(t3)                
            self.display_objs.append(t3)

        btext = "LAUNCH"
        if self.scene.game.input_mode == "joystick":
            btext = "[*x*] LAUNCH"
        b = Button(V2(res.x - 30, res.y - 30), btext, "huge", self.click_launch)
        b.offset = (1, 1)
        b.fade_in()
        self.scene.ui_group.add(b)
        self.joy_current_confirm_button = b
        self.display_objs.append(b)
        

    def create_shop_display(self, node):
        res = self.scene.game.game_resolution

        t1 = typewriter.Typewriter("Sector %d - [^Shop]" % node['sector'], "big", V2(60, self.scene.background.center_y + 55), PICO_WHITE, multiline_width=500)
        self.scene.ui_group.add(t1)

        btext = "SHOP"
        if self.scene.game.input_mode == "joystick":
            btext = "[*x*] SHOP"
        b = Button(V2(res.x - 30, res.y - 30), btext, "huge", self.click_store)
        b.offset = (1, 1)
        b.fade_in()
        self.scene.ui_group.add(b)
        self.joy_current_confirm_button = b
        self.display_objs = [t1,b]

class StoreNodeState(states.UIEnabledState):
    def __init__(self, store_data, scene):
        super().__init__(scene)
        self.store_data = store_data

    def enter(self):
        print("enter")
        super().enter()
        self.panel = storepanel.StorePanel(self.store_data, V2(0,0), self)
        self.scene.ui_group.add(self.panel)
        self.panel.add_all_to_group(self.scene.ui_group)
