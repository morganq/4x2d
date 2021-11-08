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
from colors import *
from economy import Resources
from explosion import Explosion
from multiplayer import inputstates
from multiplayer.levelstates import MultiplayerNormalState
from planet.planet import Planet
from v2 import V2

PLAYER_COLORS = [
    PICO_BLUE,
    PICO_ORANGE,
    PICO_GREEN,
    PICO_PINK
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

    def load_level(self, file):
        # Make a homeworld for each player
        for i, civ in enumerate(self.player_civs):
            p = Planet(self, HOMEWORLD_POSITIONS[self.num_players][i] + self.game.game_offset, 7, Resources(100,0,0))
            p.change_owner(civ)
            p.add_population(5)
            p.add_ship("fighter")
            p.add_ship("fighter")
            civ.homeworld = p
            self.game_group.add(p)

        self.objgrid.generate_grid(self.get_objects_initial())

    def setup_players(self):
        self.meters = {}
        # Make a civ for each player
        for i in range(self.num_players):
            pp = (UI_POSITIONS[self.num_players][i] - V2(0.5,0.5))
            pp = V2(pp.x * 400, pp.y * 390) + self.game.game_resolution / 2
            c = civ.MultiplayerCiv(self, pp)
            c.color = PLAYER_COLORS[i]
            self.player_civs.append(c)
            self.player_input_sms[(i+1)] = states.Machine(inputstates.CursorState(self, c, self.game.player_inputs[i].input_type))

            uipos = UI_POSITIONS[self.num_players][i]
            if uipos.x == 1:
                uipos.x = self.game.game_resolution.x - 104
            if uipos.y == 1:
                uipos.y = self.game.game_resolution.y - 45

            self.meters[c] = {}
            for j,r in enumerate(['iron', 'ice', 'gas']):
                self.meters[c][r] = meter.Meter(V2(uipos.x + 19,uipos.y + 3 + j * 14), 80, 9, economy.RESOURCE_COLORS[r], c.upgrade_limits.data[r], tick_x=120)
                self.meters[c][r].stay = True
                self.ui_group.add(simplesprite.SimpleSprite(V2(uipos.x + 6,uipos.y + 2 + j * 14), "assets/i-%s.png" % r))
                self.ui_group.add(self.meters[c][r])

        self.radar = Explosion(V2(300, 180), [PICO_GREEN], 1.25, self.game.game_resolution.x)
        self.ui_group.add(self.radar)            

    def get_player_id(self, civ):
        i = self.player_civs.index(civ)
        return i+1

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

    def get_starting_state(self):
        return MultiplayerNormalState(self)

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

    def take_player_input(self, player_id, inp, event):
        self.player_input_sms[player_id].state.take_input(inp, event)

    def player_click_upgrade(self, civ):
        pid = self.get_player_id(civ)
        #self.player_input_sms[pid].transition(inputstates.UpgradeState(self, civ, self.game.player_inputs[pid-1].input_type))
