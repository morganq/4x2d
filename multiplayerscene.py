from collections import defaultdict

import pygame

import button
import civ
import economy
import fleet
import flowfield
import levelscenebase
import meter
import pauseoverlay
import simplesprite
import stagename
import states
import text
from colors import *
from economy import RESOURCE_COLORS, Resources
from explosion import Explosion
from multiplayer import inputstates
from multiplayer.levelstates import MultiplayerNormalState
from multiplayer.multiplayerlevelcontroller import MultiplayerLevelController
from planet.planet import Planet

V2 = pygame.math.Vector2

PLAYER_COLORS = [
    PICO_BLUE,
    PICO_ORANGE,
    PICO_GREEN,
    PICO_PINK
]
PLAYER_NAMES = [
    'Blue', 'Orange', 'Green', 'Pink'
]

# Preset positions based on the number of players
HOMEWORLD_POSITIONS = {
    1: (V2(50,50)), # 1 Player: top left (not intended to be used really)
    2: (V2(50, 50), V2(560,310)), # 2 Player positions: top left and bottom right
    3: (V2(50, 320), V2(300, 50), V2(560,310)), # 3 Player positions: bottom left, top middle, bottom right
    4: (V2(50, 50), V2(50, 310), V2(560, 50), V2(560,310)) # 4 Player positions: corners
}

# Preset for UI
UI_POSITIONS = {
    1: (V2(0,0)),
    2: (V2(0,0), V2(1, 1)),
    3: (V2(0,0), V2(1, 0), V2(1,1)),
    4: (V2(0,0), V2(0, 1), V2(1,0), V2(1, 1)),
}

class MultiplayerScene(levelscenebase.LevelSceneBase):
    def __init__(self, game, num_players):
        super().__init__(game, "choke")
        self.num_players = num_players
        self.player_civs = []
        self.player_input_sms = {}
        self.player_upgrade_buttons = {}
        self.player_upgrade_texts = {}
        self.player_targets = {}
        self.player_game_speed_inputs = {}
        self.victory_number = 9001

    def load_level(self, file):
        # Make a homeworld for each player
        for i, civ in enumerate(self.player_civs):
            p = Planet(self, HOMEWORLD_POSITIONS[self.num_players][i] + self.game.game_offset, 8, Resources(100,0,0))
            p.change_owner(civ)
            p.add_population(6)
            p.add_ship("fighter")
            p.add_ship("fighter")
            civ.homeworld = p
            self.game_group.add(p)

        center = V2(self.game.game_resolution / 2)
        mid = Planet(self, center, 3, Resources(100,0,0))
        mid.set_time_loop()
        self.game_group.add(mid)

        self.objgrid.generate_grid(self.get_objects_initial())

    def setup_players(self):
        self.meters = {}
        # Make a civ for each player
        for i in range(self.num_players):
            uipos = UI_POSITIONS[self.num_players][i]
            if uipos.x == 1:
                uipos.x = self.game.game_resolution.x - 104
            if uipos.y == 1:
                uipos.y = self.game.game_resolution.y - 60
            c = civ.MultiplayerCiv(self, uipos)
            c.worker_loss = 1
            c.color = PLAYER_COLORS[i]
            c.name = PLAYER_NAMES[i]
            self.player_civs.append(c)
            self.player_input_sms[i] = states.Machine(inputstates.CursorState(self, c, self.game.player_inputs[i].input_type))
            self.player_game_speed_inputs[c] = 0

            self.meters[c] = {}
            for j,r in enumerate(['iron', 'ice', 'gas']):
                self.meters[c][r] = meter.Meter(V2(uipos.x + 19,uipos.y + 3 + j * 14), 80, 9, economy.RESOURCE_COLORS[r], c.upgrade_limits.data[r], tick_x=120)
                self.meters[c][r].stay = True
                self.ui_group.add(simplesprite.SimpleSprite(V2(uipos.x + 6,uipos.y + 2 + j * 14), "assets/i-%s.png" % r))
                self.ui_group.add(self.meters[c][r])

            bp = None
            if uipos.x < self.game.game_resolution.x / 2:
                bp = V2(uipos.x + 110, uipos.y + 5)
            else:
                bp = V2(uipos.x - 50, uipos.y + 5)

            ub = button.Button(
                bp,
                "Up",
                "small",
                (lambda c:(lambda:self.player_mouse_click_upgrade(c)))(c), # Closure to capture civ
                None,
                None,
                "assets/i-iron.png",
                PICO_LIGHTGRAY,
                fixed_width=46
            )
            ub.visible = False
            self.ui_group.add(ub)
            self.player_upgrade_buttons[i] = ub
            ut = text.Text("", "small", bp + V2(24,22), shadow=PICO_BLACK)
            ut.offset = (0.5, 0)
            self.ui_group.add(ut)
            self.player_upgrade_texts[i] = ut

            # target
            target = text.Text("", "small", uipos + V2(6, 44), shadow=PICO_BLACK, multiline_width=200)
            self.ui_group.add(target)
            self.player_targets[i] = target

        self.radar = Explosion(V2(300, 180), [PICO_GREEN], 1.25, self.game.game_resolution.x)
        self.ui_group.add(self.radar)            

    def get_player_id(self, civ):
        i = self.player_civs.index(civ)
        return i

    def get_civ_sm(self, civ):
        return self.player_input_sms[self.get_player_id(civ)]

    def add_ui_elements(self):
        self.pause_sprite = pauseoverlay.PauseOverlay()
        self.pause_sprite.layer = 5
        self.ui_group.add(self.pause_sprite)

        self.stage_name = stagename.StageName(V2(0, 100), 999, "Multiplayer", "Zxmcnvrqwyoizopxcmasdf")
        self.ui_group.add(self.stage_name)

    def load(self):
        self.create_layers()        

        self.difficulty = 20
        
        self.setup_players()

        if self.levelfile:
            self.load_level(self.levelfile)
        else:
            self.load_level("choke")
        
        self.add_extra_spaceobjects()
        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])
        self.background.generate_image(self.objgrid)
        self.add_ui_elements()    

        self.fleet_managers = {}
        for civ in self.player_civs:
            self.fleet_managers[civ] = fleet.FleetManager(self, civ)

        print("generate flowfield")
        self.flowfield = flowfield.FlowFieldMap()
        self.flowfield.generate(self)
        self.flowfielddebug = 0
        self.flowfielddebugstage = 0

        self.fleet_diagram.generate_image(self)

        #self.game.game_speed_input = 1
        self.stage_name.kill()

        self.level_controller = MultiplayerLevelController(self)

    def get_starting_state(self):
        return MultiplayerNormalState(self)

    def get_enemy_civs(self, civ):
        return [c for c in self.player_civs if c != civ]

    def get_fleet_manager(self, civ):
        return self.fleet_managers[civ]        

    def update(self, dt):
        dt = min(dt,0.1)
        
        if self.cinematic:
            self.game_speed = 1.0
        else:
            self.game_speed = sum(self.player_game_speed_inputs.values()) / len(self.player_civs) * 5 + 1

        self.update_game(dt * self.game_speed, dt)
        self.update_ui(dt)

    def update_game(self, dt, base_dt):
        for sm in self.player_input_sms.values():
            sm.state.update(dt)

        for civ in self.player_civs:
            civ.update(dt)

        for manager in self.fleet_managers.values():
            manager.update(dt)

        return super().update_game(dt, base_dt)

    def update_ui(self, dt):
        super().update_ui(dt)

        for civ in self.player_civs:
            for res_type in civ.upgrade_limits.data.keys():
                ratio = civ.upgrade_limits.data[res_type] / civ.base_upgrade_limits.data[res_type]
                #self.meters[civ][res_type].set_width(80 * ratio)
                self.meters[civ][res_type].max_value = civ.upgrade_limits.data[res_type]
                self.meters[civ][res_type].value = civ.resources.data[res_type]      

            self.player_targets[self.get_player_id(civ)].set_text("%d to win" % (self.victory_number - civ.total_mined))

    def take_player_input(self, player_id, inp, event):
        self.player_input_sms[player_id].state.take_input(inp, event)

    def player_mouse_click_upgrade(self, civ):
        if self.game.player_inputs[self.get_player_id(civ)].input_type == "mouse":
            self.player_click_upgrade(civ)

    def player_click_upgrade(self, civ):
        pid = self.get_player_id(civ)
        self.player_input_sms[pid].transition(inputstates.UpgradeState(self, civ, self.game.player_inputs[pid].input_type))

    def update_upgrade_ui(self, civ):
        pid = self.get_player_id(civ)
        b = self.player_upgrade_buttons[pid]
        if len(civ.upgrades_stocked) > 0:
            res_type = civ.upgrades_stocked[0]
            b.icon = "assets/i-%s.png" % res_type
            b.color = RESOURCE_COLORS[res_type]
            b._generate_image()
            b.visible = True
        else:
            b.visible = False
        if len(civ.upgrades_stocked) > 1:
            self.player_upgrade_texts[pid].set_text("+%d More" % (len(civ.upgrades_stocked) - 1))
        else:
            self.player_upgrade_texts[pid].set_text("")

    def show_player_upgrade_button(self, civ, res_type):
        self.update_upgrade_ui(civ)

    def finish_player_upgrade(self, civ):
        self.update_upgrade_ui(civ)
