import json
import random
import sys
import time
import traceback
from collections import defaultdict

import pygame

import aliens
import fleet
import fleetdiagram
import flowfield
import funnotification
import game
import levelcontroller
import levelscenebase
import levelstates
import o2meter
import optimize
import pauseoverlay
import scene
import simplesprite
import sound
import stagename
import states
import text
import upgradestate
import upkeepindicator
from aliens import bosslevelcontroller, bossmothership, bosstimecrystal
from asteroid import Asteroid
from button import Button
from civ import Civ, PlayerCiv
from colors import *
from debug import debug_render
from economy import RESOURCE_COLORS, RESOURCES, Resources
from explosion import Explosion
from hazard import Hazard
from helper import all_nearby, get_nearest
from levelbackground import LevelBackground
from line import AssetLine, Line
from meter import Meter
from objgrid import ObjGrid
from planet.planet import Planet
from resources import resource_path
from ships import scout
from ships.ship import Ship
from spaceobject import SpaceObject
from text import FONTS, Text, render_multiline_to
from upgrade.upgradeicon import UpgradeIcon
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2

TICK_TIME = 0.05

class LevelScene(levelscenebase.LevelSceneBase):
    def __init__(self, game, levelfile, alienrace, difficulty, stage_num, title, description, options=None):
        levelscenebase.LevelSceneBase.__init__(self, game, levelfile)
        self.options = options
        self.animation_timer = 0
        self.player_civ = PlayerCiv(self)
        self.alienrace = alienrace
        self.difficulty = difficulty
        self.stage_num = stage_num
        self.title = title
        self.description = description

        self.paused = False
        self.cinematic = False
        self.game_speed = 1.0
        self.time = 0
        self.debug = False
        self._score = 0
        self.is_tutorial = False
        self.update_times = defaultdict(lambda:0)
        self.asset_buttons = []

        self.update_remainder_time = 0
        self.level_controller = None

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value

    def load_level(self, levelfile):
        print("load level")
        data = json.load(open(resource_path("levels/%s.json" % levelfile)))
        for obj in data:
            t = None
            owner = None
            if obj['type'].endswith("planet"):
                t = "planet"
                if obj['type'] == "my_planet": owner = self.player_civ
                elif obj['type'] == "enemy_planet": owner = self.enemy.civ
            if t == "planet":
                r = [v * 10 for v in obj['data']['resources']]
                pos = V2(*obj['pos'])
                o = Planet(self, pos + self.game.game_offset, obj['size'], Resources(*r))
                if owner and not owner.homeworld:
                    owner.homeworld = o
                if owner:
                    o.change_owner(owner)
                    o.population = 1
                
            elif obj['type'] == "hazard":
                pos = V2(*obj['pos'])
                o = Hazard(self, pos + self.game.game_offset, obj['size'])
            elif obj['type'] == "crystal":
                pos = V2(*obj['pos'])
                r = [v * 10 for v in obj['data']['resources']]
                o = bosstimecrystal.TimeCrystal(self, pos + self.game.game_offset, 2, Resources(*r))       
                o.change_owner(self.enemy.civ)         
                o.generate_stranded_ships()
            else:
                print(obj)
            self.game_group.add(o)
        self.objgrid.generate_grid(self.get_objects_initial())

    def setup_players(self):
        # Me
        self.homeworld = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.player_civ))[0]
        self.homeworld.population = 3 + self.game.run_info.bonus_population
        self.homeworld.ships['fighter'] = 1 + self.game.run_info.bonus_fighters

        self.radar = Explosion(self.homeworld.pos, [PICO_GREEN], 1.25, self.game.game_resolution.x)
        self.ui_group.add(self.radar)

        # Alien
        p = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.enemy.civ))[0]
        p.population = 5

    def add_ui_elements(self):
        self.meters = {}
        self.upgrade_texts = {}
        for i,r in enumerate(self.player_civ.resources.data.keys()):
            self.meters[r] = Meter(V2(19,3 + i * 14), 120, 9, RESOURCE_COLORS[r], self.player_civ.upgrade_limits.data[r], tick_x=120)
            self.meters[r].stay = True
            self.ui_group.add(simplesprite.SimpleSprite(V2(6,2 + i * 14), "assets/i-%s.png" % r))
            self.ui_group.add(self.meters[r])
            self.upgrade_texts[r] = Text("", "small", V2(144, 4 + i * 14), multiline_width=200)
            self.ui_group.add(self.upgrade_texts[r])

        self.player_civ.resources.on_change(self.on_civ_resource_change)

        upy = 80
        self.saved_upgrade_buttons = {}
        for u in self.game.run_info.saved_technologies + self.game.run_info.blueprints:
            upicon = UpgradeIcon(V2(-2, upy), u, self.on_click_saved_upgrade, tooltip=True)
            self.saved_upgrade_buttons[u] = upicon
            self.ui_group.add(upicon)
            upy += 27

        if game.DEV:
            self.ui_group.add(Button(V2(self.game.game_resolution.x - 50, self.game.game_resolution.y - 20), 'Win', 'small', self.dev_win))
            self.ui_group.add(Button(V2(self.game.game_resolution.x - 110, self.game.game_resolution.y - 20), 'Lose', 'small', self.dev_lose))

        self.o2_meter = o2meter.O2Meter(V2(self.game.game_resolution.x - 86, 6))
        
        if self.options == "oxygen":
            self.game.run_info.o2 = 0

        self.o2_meter.o2 = self.game.run_info.o2
        self.o2_meter._generate_image()
        self.ui_group.add(self.o2_meter)    

        self.stage_name = stagename.StageName(V2(0, 100), self.stage_num, self.title, self.description)
        self.ui_group.add(self.stage_name)
        if self.title == "":
            self.stage_name.kill()

        self.upkeep_indicator = upkeepindicator.UpkeepIndicator(self)
        self.ui_group.add(self.upkeep_indicator)

        self.pause_sprite = pauseoverlay.PauseOverlay()
        self.pause_sprite.layer = 5
        self.ui_group.add(self.pause_sprite)
        self.game.game_speed_input = 0

    def setup_mods(self):
        galaxy = self.game.run_info.get_current_level_galaxy()
        if not galaxy['mods']:
            return
        mod = galaxy['mods'][0] # only 1 for now
        if mod == "warp_drive":
            self.enemy.civ.base_stats['warp_drive'] = 5
        elif mod == "big_planet":
            p = self.get_civ_planets(self.enemy.civ)[0]
            p.size += 10
            p.regenerate_art()
        elif mod == "reflector":
            for planet in self.get_civ_planets(self.enemy.civ):
                planet.add_building(UPGRADE_CLASSES["b_defense1"])
        elif mod == "ship_shield_far_from_home":
            self.enemy.civ.base_stats['ship_shield_far_from_home'] = 5
        elif mod == "atomic_bomb":
            self.enemy.civ.base_stats['atomic_bomb'] = 1
        elif mod == "battleship":
            p = self.get_civ_planets(self.enemy.civ)[0]
            p.add_ship("%sbattleship" % galaxy['alien'])

    def load(self):
        print("load")
        self.create_layers()
        civ_name = self.game.run_info.get_current_level_galaxy()['alien']
        if self.alienrace:
            civ_name = self.alienrace
        AlienClass = aliens.alien.ALIENS[civ_name]
        self.enemies = [AlienClass(self, Civ(self))]
        self.enemy = self.enemies[0]        
        
        if self.levelfile:
            self.load_level(self.levelfile)
        else:
            self.load_level("choke")

        if self.difficulty == 9:
            self.level_controller = bosslevelcontroller.BossLevelController(self)
        else:
            self.level_controller = levelcontroller.LevelController(self)

        self.setup_players()
        self.add_extra_spaceobjects()
        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])
        print("generate image")
        self.background.generate_image(self.objgrid)
        print("done generate image")
        self.add_ui_elements()    

        

        self.fleet_managers = {
            'my':fleet.FleetManager(self, self.player_civ),
            'enemy':fleet.FleetManager(self, self.enemy.civ)
        }

        print("generate flowfield")
        self.flowfield = flowfield.FlowFieldMap()
        self.flowfield.generate(self)
        self.flowfielddebug = 0
        self.flowfielddebugstage = 0

        self.fleet_diagram.generate_image(self)

        self.enemy.set_difficulty(self.difficulty)
        self.setup_mods()

        # Add the time loops
        if self.difficulty >= 6 and self.difficulty < 9:
            planets = [s for s in self.get_objects_initial() if isinstance(s, Planet) and s.owning_civ == None and s.time_loop == False]
            if planets:
                planets.sort(key=lambda x:x.pos.x)
                for i in range(1):
                    p = planets.pop(int(len(planets) / 2))
                    #p.set_time_loop()

        if self.options == "surround":
            for planet in self.get_civ_planets(None):
                planet.change_owner(self.enemy.civ)
            self.enemy.civ.resources.set_resource("gas", 220)

        if self.options == "performance":
            from aliens.alien1fighter import Alien1Fighter
            for i in range(30):
                #civ = self.player_civ if i % 2 == 0 else self.enemy.civ
                civ = self.enemy.civ
                p = V2(random.randint(50, self.game.game_resolution.x-50), random.randint(50, self.game.game_resolution.y-50))
                s = Alien1Fighter(self, p, civ)
                self.game_group.add(s)
                random_planet = random.choice(self.get_planets())
                s.set_target(random_planet)

        if self.options == "rich":
            self.player_civ.resources.set_resource("iron", 1150)
            self.player_civ.resources.set_resource("ice", 1150)
            self.player_civ.resources.set_resource("gas", 1150) 

        if self.options == "gas":
            self.player_civ.resources.set_resource("gas", 1150)                                        

        if self.options == "fighters":
            for i in range(20):
                self.homeworld.add_ship("fighter")    

    def get_fleet_manager(self, civ):
        if civ == self.player_civ:
            return self.fleet_managers['my']
        return self.fleet_managers['enemy']

    def on_click_help(self):
        self.sm.transition(levelstates.HelpState(self))

    def on_click_upgrade(self):
        self.sm.transition(upgradestate.UpgradeState(self))
        sound.play("click1")

    def on_click_saved_upgrade(self, upgrade):
        st = upgradestate.SavedUpgradeState(self)
        self.sm.transition(st)
        st.on_select(upgrade)

    def invalidate_saved_upgrade(self, upgrade):
        self.saved_upgrade_buttons[upgrade.name].kill()

    def get_enemy_civs(self, civ):
        if civ == self.player_civ:
            return [self.enemy.civ]
        else:
            return [self.player_civ]

    def dev_win(self):
        for planet in self.get_civ_planets(self.enemy.civ):
            planet.take_damage(99999, origin=None)
            if not isinstance(planet, bosstimecrystal.TimeCrystal):
                pass
                #planet.change_owner(self.player_civ)
                #planet.add_population(3)
                #planet.add_ship("fighter")

    def dev_lose(self):
        for planet in self.get_civ_planets(self.player_civ):
            planet.take_damage(99999, origin=None)        

    def on_civ_resource_change(self, res_type, val):
        pass

    def get_starting_state(self):
        return levelstates.BeginState(self)

    def update_ui(self, dt):
        levelscenebase.LevelSceneBase.update_ui(self, dt)

        for res_type in self.player_civ.upgrade_limits.data.keys():
            ratio = self.player_civ.upgrade_limits.data[res_type] / self.player_civ.base_upgrade_limits.data[res_type]
            self.upgrade_texts[res_type].x = 120 * ratio + 20
            self.meters[res_type].set_width(120 * ratio)
            self.meters[res_type].max_value = self.player_civ.upgrade_limits.data[res_type]
            self.meters[res_type].value = self.player_civ.resources.data[res_type]

    def update_game(self, dt, base_dt):
        ut = time.time()
        self.update_times = defaultdict(lambda:0)
        if self.paused:
            self.sm.state.paused_update(base_dt)
            return        

        self.time += dt

        if self.level_controller:
            self.level_controller.update(dt)

        if self.time > 300 and not self.player_civ.scarcity:
            self.player_civ.enable_scarcity()
            self.enemy.civ.enable_scarcity()
            fn = funnotification.FunNotification("SCARCITY! Upgrade costs increased")
            self.ui_group.add(fn)
            
        self.game.run_info.o2 -= dt
        #if self.time % 1 < (self.time - dt) % 1:
        self.o2_meter.o2 = self.game.run_info.o2
        self.o2_meter._generate_image()

        scene.Scene.update(self, dt)

        # update object grid
        t = time.time()
        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])
        self.update_times["objgrid"] = time.time() - t

        for sprite in self.background_group.sprites():
            t = time.time()
            sprite.update(dt)
            elapsed = time.time() - t
            self.update_times[type(sprite)] += elapsed

        # damnit... issue is double collisions etc.
        #self.update_remainder_time += dt
        #ticks = int(self.update_remainder_time // TICK_TIME)
        #print("ticks", ticks)
        #for i in range(ticks):
        #    self.update_remainder_time -= TICK_TIME
        #    self.update_game_objects(TICK_TIME)
        #    self.update_collisions(TICK_TIME)
        self.update_game_objects(dt)
        self.update_collisions(dt)

        if not self.cinematic and not self.is_tutorial:
            for enemy in self.enemies:
                enemy.update(dt)
        
        t = time.time()
        self.fleet_managers['my'].update(dt)
        self.fleet_managers['enemy'].update(dt)
        #self.fleet_diagram.generate_image(self)
        self.update_times['fleets'] = time.time() - t

        self.flowfield.update(dt)

        t = time.time()
        self.player_civ.update(dt)
        for enemy in self.enemies:
            enemy.civ.update(dt)
        self.update_times['civs'] = time.time() - t

        self.update_times['update'] = time.time() - ut
        
    def update_asset_buttons(self):
        for i,button in enumerate(self.asset_buttons):
            button.pos = V2(self.game.game_resolution.x / 2 - i * 8 - 30, self.game.game_resolution.y - 4)
            self.ui_group.change_layer(button, -i)
            if i == 0:
                button.onclick = self.on_click_upgrade
                #button.y -= 2
            else:
                button.onclick = None
            
    def add_asset_button(self, resource):
        button = Button(V2(self.game.game_resolution.x / 2, self.game.game_resolution.y - 4), "UPGRADE", "big", None, asset_border=True, fixed_width=90)
        text = "%s" % resource.upper()
        button.text = text
        if self.game.input_mode == "joystick":
            button.joy_button = "[*triangle*]"
        else:
            button.joy_button = None
        button.label = "UPGRADE"
        button.icon = "assets/i-%s.png" % resource
        color = RESOURCE_COLORS[resource]
        if resource == "iron":
            button.color = PICO_LIGHTGRAY
        else:
            button.color = RESOURCE_COLORS[resource]
        button._generate_image()        
        button.offset = (0, 1)
        button._recalc_rect()
        button.visible = 1
        button.layer = 0
        button.fade_in(2)
        self.ui_group.add(button) 
        self.asset_buttons.append(button)  
        self.update_asset_buttons()    

        y1 = self.meters[resource].y + 4
        y2 = button.get_center().y
        x2 = button.top_left.x
        l1 = AssetLine(V2(3,y1), V2(6, y1), color)
        l2 = AssetLine(V2(3,y1), V2(3, y2), color)
        l3 = AssetLine(V2(3, y2), V2(x2, y2), color)
        l1.next_line = l2
        l2.next_line = l3
        l1.start()
        for line in [l1,l2,l3]:
            self.ui_group.add(line)
        

    def pop_asset_button(self):
        btn = self.asset_buttons.pop(0)
        self.ui_group.remove(btn)
        self.update_asset_buttons()

    def render(self):
        t = time.time()
        #self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        if game.DEV:
            for spr in self.background_group.sprites() + self.game_group.sprites() + self.ui_group.sprites():
                if spr.image is None and spr.visible:
                    print(spr, "bad image")
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        if self.debug:
            for k,v in self.fleet_managers.items():
                for fleet in v.current_fleets:
                    fleet.debug_render(self.game.screen)

            gi = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
            gi.fill((0,0,0,0))
            ff = list(self.flowfield.fields.values())[self.flowfielddebug]
            if self.flowfielddebugstage > 0:
                for col in range(1, len(ff.base_grid[0])):
                    x = col * flowfield.GRIDSIZE + ff.offset.x
                    pygame.draw.line(gi, (255,255,255,50), (x, ff.offset.y), (x, ff.offset.y + game.RES[1]), 1)
                for row in range(1, len(ff.base_grid)):
                    y = row * flowfield.GRIDSIZE + ff.offset.y
                    pygame.draw.line(gi, (255,255,255,50), (ff.offset.x, y), (ff.offset.x + game.RES[0], y), 1)                
            if self.flowfielddebugstage == 1:
                for y,gr in enumerate(ff.base_grid):
                    for x,gc in enumerate(gr):     
                        pt = V2(x * flowfield.GRIDSIZE, y * flowfield.GRIDSIZE) + ff.offset
                        s = "-"
                        if gc:
                            s = "O"
                        FONTS['tiny'].render_to(gi, (pt.x + 2, pt.y + 2), s, (128,255,128,180))

            if self.flowfielddebugstage == 2:
                for y,gr in enumerate(ff.dgrid):
                    for x,gc in enumerate(gr):     
                        pt = V2(x * flowfield.GRIDSIZE, y * flowfield.GRIDSIZE) + ff.offset
                        if isinstance(gc, tuple):
                            s = "-"
                        elif gc is None:
                            s = "??"
                        else:
                            s = str(gc % 10)
                        FONTS['tiny'].render_to(gi, (pt.x + 2, pt.y + 2), s, (128,255,128,180))
                        
            elif self.flowfielddebugstage == 3:
                for y,gr in enumerate(ff.grid):
                    for x,gc in enumerate(gr):
                        p1 = V2((x + 0.5) * flowfield.GRIDSIZE, (y + 0.5) * flowfield.GRIDSIZE) + ff.offset
                        if gc is not None:
                            p2 = p1 + gc * flowfield.GRIDSIZE * 0.75
                            pygame.draw.line(gi, (0,0,255), p1.tuple(),p2.tuple())
                            pygame.draw.circle(gi, (0,0,255), p1.tuple(), 1)
                        else:
                            pygame.draw.circle(gi, (255,0,255), p1.tuple(), 3, 1)
            
            if False:
                for y in range(len(self.objgrid.grid)):
                    for x in range(len(self.objgrid.grid[0])):
                        x1 = x * self.objgrid.grid_size
                        y1 = y * self.objgrid.grid_size
                        pygame.draw.rect(gi, (0,255,0,150), (x1,y1,self.objgrid.grid_size+1, self.objgrid.grid_size+1), 1)
                        FONTS['tiny'].render_to(gi, (x1 + 2, y1 + 2), "%d" % len(self.objgrid.grid[y][x]), (128,255,128,180))

            self.game.screen.blit(gi, (0,0))
        
        self.pause_sprite.visible = self.paused
        if self.stage_name.time < 2 and self.stage_name.alive():
            self.pause_sprite.visible = False

        if not self.cinematic:
            self.ui_group.draw(self.game.screen)
            self.tutorial_group.draw(self.game.screen)
        if self.debug:
            self.enemy.render(self.game.screen)
            debug_render(self.game.screen, self)

        self.update_times['render'] = time.time() - t

        #FONTS['small'].render_to(self.game.screen, (5,game.RES[1] - 25), "%d" % self.time, (255,255,255,255))
        if self.debug:
            for i,s in enumerate(["%s:%.1f" % (a,b * 1000) for a,b in self.update_times.items()]):
                FONTS['tiny'].render_to(self.game.screen, (30, 100 + i * 8), s, (128,255,128,180))

            FONTS['tiny'].render_to(self.game.screen, (30, 50),
                "diagram: %.1f MAX, %.1f MEAN" % (self.fleet_diagram.max_debug_time * 1000, self.fleet_diagram.mean_debug_time * 1000),
                (128,255,255,180)
            )

        if game.DEV:
            FONTS['tiny'].render_to(self.game.screen, (game.RES[0] - 20, 20), "%d" % self.time, (128,255,128,180))

        res = self.game.game_resolution
        if self.cinematic:
            surf = pygame.Surface(res.tuple(), pygame.SRCALPHA)
            pygame.draw.rect(surf, PICO_DARKBLUE, (0,0,res.x,40), 0)
            pygame.draw.rect(surf, PICO_DARKBLUE, (0,res.y-40,res.x,40), 0)
            #surf.set_alpha(160)
            self.game.screen.blit(surf, (0,0))


        tri = [V2(0,0), V2(4,4), V2(0,8)]
        if self.game_speed > 1:
            color = PICO_BLUE if ((self.time % 2) > 1) else PICO_WHITE
            
            pygame.draw.rect(self.game.screen, PICO_BLUE, (0, 0, res.x, res.y), 1)
            
            pygame.draw.polygon(self.game.screen, color, [(z + V2(res.x - 12, res.y - 12)).tuple() for z in tri], 0)
            pygame.draw.polygon(self.game.screen, color, [(z + V2(res.x - 7, res.y - 12)).tuple() for z in tri], 0)

        elif not self.cinematic:
            ctl = "Space"
            if self.game.input_mode == "joystick":
                ctl = "R1"
            t = text.render_multiline(ctl, "small", PICO_LIGHTGRAY, wrap_width=130)
            self.game.screen.blit(t, (res.x - t.get_width() - 16, res.y - 12))
            pygame.draw.polygon(self.game.screen, PICO_LIGHTGRAY, [(z + V2(res.x - 12, res.y - 12)).tuple() for z in tri], 0)
            pygame.draw.polygon(self.game.screen, PICO_LIGHTGRAY, [(z + V2(res.x - 7, res.y - 12)).tuple() for z in tri], 0)            
            #FONTS['small'].render_to(self.game.screen, PICO_BLUE, "")

        return None

    def update_run_stats(self):
        self.game.run_info.time_taken += self.time
        self.game.run_info.ships_lost += self.player_civ.ships_lost
