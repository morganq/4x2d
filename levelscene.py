import json
import random
import sys
import time
import traceback
from collections import defaultdict

import pygame

import aliens
import fleet
import flowfield
import funnotification
import game
import levelstates
import o2meter
import optimize
import scene
import simplesprite
import sound
import states
import upgradestate
from asteroid import Asteroid
from background import Background
from button import Button
from civ import Civ, PlayerCiv
from colors import *
from debug import debug_render
from economy import RESOURCE_COLORS, RESOURCES, Resources
from hazard import Hazard
from helper import all_nearby, get_nearest
from meter import Meter
from objgrid import ObjGrid
from planet.planet import Planet
from resources import resource_path
from ships.ship import Ship
from spaceobject import SpaceObject
from text import FONTS, Text
from upgrade.upgradeicon import UpgradeIcon
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2


class LevelScene(scene.Scene):
    def __init__(self, game, levelfile, alienrace, difficulty, options=None):
        scene.Scene.__init__(self, game)
        self.options = options
        self.animation_timer = 0
        self.my_civ = PlayerCiv(self)
        self.levelfile = levelfile
        self.alienrace = alienrace
        self.difficulty = difficulty

        self.paused = False
        self.game_speed = 1.0
        self.time = 0
        self.debug = False
        self._score = 0
        self.is_tutorial = False
        self.update_times = defaultdict(lambda:0)

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        # TODO: get rid of

    def random_object_pos(self):
        pos = None
        while pos is None:
            pos = V2(random.randint(30, game.RES[0] - 30), random.randint(30, game.RES[1] - 30))
            
            near_button = pygame.Rect(game.RES[0] / 2 - 100, game.RES[1] - 60, 200, 60)
            if near_button.collidepoint(*pos.tuple()):
                pos = None
                continue

            near_meters = pygame.Rect(0, 0, 250, 60)
            if near_meters.collidepoint(*pos.tuple()):
                pos = None
                continue

            dist = 999999
            for obj in self.get_objects_initial():
                delta = (obj.pos - pos).sqr_magnitude()
                if delta < dist:
                    dist = delta
            if dist <= 30 ** 2:
                pos = None
                continue

            
        return pos

    def give_building(self, planet, upgrade):
        planet.add_building(upgrade)
        planet.owning_civ.researched_upgrade_names.add(upgrade.name)

    def load_level(self, levelfile):
        data = json.load(open(resource_path("levels/%s.json" % levelfile)))
        for obj in data:
            t = None
            owner = None
            if obj['type'].endswith("planet"):
                t = "planet"
                if obj['type'] == "my_planet": owner = self.my_civ
                elif obj['type'] == "enemy_planet": owner = self.enemy.civ
            if t == "planet":
                r = [v * 10 for v in obj['data']['resources']]
                o = Planet(self, V2(*obj['pos']), obj['size'], Resources(*r))
                if owner:
                    o.change_owner(owner)
                
            elif obj['type'] == "hazard":
                o = Hazard(self, V2(*obj['pos']), obj['size'])
            self.game_group.add(o)
        self.objgrid.generate_grid(self.get_objects_initial())

    def create_layers(self):
        self.objgrid = ObjGrid(game.RES[0], game.RES[1], 50)
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()

        self.background_group.add(Background(V2(0,0)))

    def setup_players(self):
        # Me
        self.homeworld = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.my_civ))[0]
        self.homeworld.population = 3 + self.game.run_info.bonus_population
        self.homeworld.ships['fighter'] = 1 + self.game.run_info.bonus_fighters

        # Alien
        p = get_nearest(V2(0, game.RES[1]), self.get_civ_planets(self.enemy.civ))[0]
        p.population = 5

    def add_extra_spaceobjects(self):
        num_planets = len(self.get_planets())

        max_planets = min(int(self.difficulty / 1.5 + 7), 16)

        separation = 70
        # TODO: Planet resources more constrained
        while num_planets < max_planets:
            avg_pos = sum([p.pos for p in self.get_planets()], V2(0,0)) / num_planets
            pos = V2(random.randint(30, game.RES[0] - 30), random.randint(30, game.RES[1] - 30))

            # If we're most of the way through creating planets, and we're on the wrong side of the avg, flip it.
            if num_planets >= max_planets * 1 / 3:
                if ((avg_pos.x < game.RES[0] / 2 and pos.x < game.RES[0] /2) or
                    (avg_pos.x > game.RES[0] / 2 and pos.x > game.RES[0] /2)):
                    pos = V2(game.RES[0] - pos.x, pos.y)
            
            near_button = pygame.Rect(game.RES[0] / 2 - 100, game.RES[1] - 60, 200, 60)
            if near_button.collidepoint(*pos.tuple()):
                continue

            near_meters = pygame.Rect(0, 0, 250, 60)
            if near_meters.collidepoint(*pos.tuple()):
                continue            
            
            dist = 999999
            for obj in self.get_objects_initial():
                delta = (obj.pos - pos).sqr_magnitude()
                if delta < dist:
                    dist = delta
            if dist > separation ** 2:
                if False: #pos.x /2 + (game.RES[1] - pos.y) < game.RES[1] - 100:
                    size = random.randint(4,7)
                    if random.random() > 0.5:
                        pr = Resources(100, 0, 0)
                    else:
                        size -= 1
                        iron = random.randint(7,10)
                        pr = Resources(iron * 10, (10 - iron) * 10, 0)
                else:
                    size = random.randint(2, 7)
                    resources = {'a':0, 'b':0, 'c':0}
                    # One resource
                    ra = random.random()
                    if ra > 0.66:
                        resources['a'] = 10
                    # Two resource
                    elif ra > 0.33:
                        resources['a'] = random.randint(5,10)
                        resources['b'] = 10 - resources['a']
                    # Three
                    else:
                        resources['a'] = random.randint(1,7)
                        resources['b'] = random.randint(1, 10 - resources['a'])
                        resources['c'] = 10 - resources['a'] - resources['b']
                    rb = random.random()
                    if rb > 0.45:
                        pr = Resources(resources['a'] * 10, resources['b'] * 10, resources['c'] * 10)
                        size += 1
                    elif rb > 0.20:
                        pr = Resources(resources['b'] * 10, resources['a'] * 10, resources['c'] * 10)
                    else:
                        pr = Resources(resources['c'] * 10, resources['b'] * 10, resources['a'] * 10)
                        size -= 1
                self.game_group.add(Planet(self, pos, size, pr))
                num_planets += 1
            else:
                separation -= 1

        for i in range(random.randint(15,20) - int(self.difficulty / 3)):
            pos = self.random_object_pos()
            self.game_group.add(Asteroid(self, pos, Resources(random.randint(20,80), random.randint(0,30), random.randint(0,10))))

    def add_ui_elements(self):
        self.meters = {}
        self.upgrade_texts = {}
        for i,r in enumerate(self.my_civ.resources.data.keys()):
            self.meters[r] = Meter(V2(15,3 + i * 14), 120, 9, RESOURCE_COLORS[r], self.my_civ.upgrade_limits.data[r])
            self.meters[r].stay = True
            self.ui_group.add(simplesprite.SimpleSprite(V2(2,2 + i * 14), "assets/i-%s.png" % r))
            self.ui_group.add(self.meters[r])
            self.upgrade_texts[r] = Text("", "small", V2(140, 4 + i * 14), multiline_width=200)
            self.ui_group.add(self.upgrade_texts[r])

        self.my_civ.resources.on_change(self.on_civ_resource_change)

        self.upgrade_button = Button(V2(game.RES[0] / 2, game.RES[1] - 4), "UPGRADE", "big", self.on_click_upgrade)
        self.upgrade_button.offset = (0.5, 1)
        self.upgrade_button._recalc_rect()
        self.upgrade_button.visible = 0
        self.ui_group.add(self.upgrade_button)

        upy = 80
        self.saved_upgrade_buttons = {}
        for u in self.game.run_info.saved_technologies + self.game.run_info.blueprints:
            print(u)
            upicon = UpgradeIcon(V2(3, upy), u, self.on_click_saved_upgrade, tooltip=True)
            self.saved_upgrade_buttons[u] = upicon
            self.ui_group.add(upicon)
            upy += 27

        if game.DEV:
            self.ui_group.add(Button(V2(2, 48), 'Win', 'small', self.dev_win))

        self.o2_meter = o2meter.O2Meter(V2(game.RES[0] - 68, 2))
        
        if self.options == "oxygen":
            self.game.run_info.o2 = 0

        self.o2_meter.o2 = self.game.run_info.o2
        self.o2_meter._generate_image()
        self.ui_group.add(self.o2_meter)    

    def load(self):
        self.create_layers()
        AlienClass = aliens.alien.ALIENS[self.game.run_info.get_path_galaxy()['alien']]
        self.enemies = [AlienClass(self, Civ(self))]
        self.enemy = self.enemies[0]        
        
        if self.levelfile:
            self.load_level(self.levelfile)
        else:
            self.load_level("choke")

        self.setup_players()
        self.add_extra_spaceobjects()
        self.add_ui_elements()    

        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])

        self.fleet_managers = {
            'my':fleet.FleetManager(self, self.my_civ),
            'enemy':fleet.FleetManager(self, self.enemy.civ)
        }

        self.flowfield = flowfield.FlowFieldMap()
        self.flowfield.generate(self)
        self.flowfielddebug = 0

        self.enemy.set_difficulty(self.difficulty)

        if self.options == "surround":
            for planet in self.get_civ_planets(None):
                planet.change_owner(self.enemy.civ)
            self.enemy.civ.resources.set_resource("gas", 220)

        if self.options == "rich":
            self.my_civ.resources.set_resource("iron", 1150)
            self.my_civ.resources.set_resource("ice", 1150)
            self.my_civ.resources.set_resource("gas", 1150) 

        if self.options == "gas":
            self.my_civ.resources.set_resource("gas", 1150)                                        

        if self.options == "fighters":
            for i in range(20):
                self.homeworld.add_ship("fighter")    

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

    def dev_win(self):
        self.sm.transition(levelstates.VictoryState(self))        

    def on_civ_resource_change(self, res_type, val):
        self.meters[res_type].max_value = self.my_civ.upgrade_limits.data[res_type]
        self.meters[res_type].value = self.my_civ.resources.data[res_type]

    def get_objects_initial(self):
        return [s for s in self.game_group.sprites() if isinstance(s,SpaceObject)]

    def get_objects(self):
        return self.objgrid.all_objects
        #return [s for s in self.game_group.sprites() if isinstance(s,SpaceObject)]

    def get_objects_in_range(self, pos, range):
        return self.objgrid.get_objects_near(pos, range)

    def get_planets(self):
        return [s for s in self.game_group.sprites() if isinstance(s,Planet)]

    def get_civ_planets(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Planet) and s.owning_civ == civ]

    def get_enemy_planets(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Planet) and s.owning_civ and s.owning_civ != civ]        

    def get_ships(self):
        return [s for s in self.get_objects() if isinstance(s,Ship)]
    
    def get_my_ships(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ == civ]

    def get_enemy_ships(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ != civ]

    def get_enemy_ships_in_range(self, civ, pos, range):
        return [s for s in self.get_objects_in_range(pos,range) if isinstance(s,Ship) and s.owning_civ != civ]        

    def get_enemy_objects(self, civ):
        return [s for s in self.get_objects() if (isinstance(s,Ship) or isinstance(s,Planet)) and s.owning_civ and s.owning_civ != civ]

    def get_civ_ships(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ == civ]        

    def get_hazards(self):
        return [s for s in self.get_objects() if isinstance(s, Hazard)]

    def get_asteroids(self):
        return [s for s in self.get_objects() if isinstance(s, Asteroid)]

    def get_starting_state(self):
        return levelstates.PlayState(self)

    def initialize_state(self):
        self.sm = states.Machine(self.get_starting_state())

    def update_layers(self):
        pass

    def start(self):
        self.load()
        self.initialize_state()
        #sound.play_music('game')  

    def update(self, dt):
        ut = time.time()
        self.update_times = defaultdict(lambda:0)
        base_dt = dt
        self.game_speed = round((self.game.game_speed_input * 3) + 1)
        dt *= self.game_speed
        if self.paused:
            self.sm.state.paused_update(dt)
            for sprite in self.ui_group.sprites():
                sprite.update(base_dt)
            return        
        self.time += dt

        if self.time > 300 and not self.my_civ.scarcity:
            self.my_civ.enable_scarcity()
            self.enemy.civ.enable_scarcity()
            fn = funnotification.FunNotification("SCARCITY! Upgrade costs increased")
            self.ui_group.add(fn)
            
        self.game.run_info.o2 -= dt
        if self.time % 1 < (self.time - dt) % 1:
            self.o2_meter.o2 = self.game.run_info.o2
            self.o2_meter._generate_image()

        scene.Scene.update(self, dt)

        # update object grid
        t = time.time()
        self.objgrid.generate_grid([s for s in self.game_group.sprites() if s.collidable])
        self.update_times["objgrid"] = time.time() - t

        
        if not self.is_tutorial:
            # Detect defeat
            if not self.get_civ_planets(self.my_civ):
                self.paused = True
                self.sm.transition(levelstates.GameOverState(self))
            
            # Detect victory
            if not self.get_civ_planets(self.enemy.civ):
                self.paused = True
                self.sm.transition(levelstates.VictoryState(self))
        
        for sprite in self.ui_group.sprites():
            t = time.time()
            sprite.update(base_dt)
            elapsed = time.time() - t
            self.update_times[type(sprite)] += elapsed

        for sprite in self.game_group.sprites() + self.background_group.sprites():
            t = time.time()
            sprite.update(dt)
            elapsed = time.time() - t
            self.update_times[type(sprite)] += elapsed

        t = time.time()
        # Collisions
        colliders = [s for s in self.get_objects() if s.collidable]
        lc = len(colliders)
        #print(lc, "colliders")
        checked = set()
        for first in colliders:
            near = self.objgrid.get_objects_near(first.pos, 50) # 50 is arbitrary...
            for second in near:
                if second in checked: # Don't double collide
                    continue
                if second == first:
                    continue
                if first.stationary and second.stationary:
                    continue
                d = first.pos - second.pos
                if d.sqr_magnitude() <= (first.collision_radius + second.collision_radius) ** 2:
                    first.collide(second)
                    second.collide(first)

            checked.add(first)

        elapsed = time.time() - t
        self.update_times["collisions"] = elapsed

        if len(self.my_civ.upgrades_stocked) > 0:
            r = self.my_civ.upgrades_stocked[0]
            text = "%s" % r.upper()
            if self.upgrade_button.visible == False or self.upgrade_button.text != text:
                self.upgrade_button.text = text
                self.upgrade_button.label = "ASSET"
                self.upgrade_button.icon = "assets/i-%s.png" % r
                self.upgrade_button.color = PICO_RED
                self.upgrade_button._generate_image()
                self.upgrade_button.fade_in(speed=2)
        else:
            if self.upgrade_button.visible:
                self.upgrade_button.visible = False

        for res_type in self.my_civ.resources.data.keys():
            num = len([u for u in self.my_civ.upgrades_stocked if u == res_type])
            if num > 0:
                self.upgrade_texts[res_type].set_text("%d asset%s available" % (num, "s" if num > 1 else ""))
            else:
                self.upgrade_texts[res_type].set_text("")

        if self.options != "pacifist":
            for enemy in self.enemies:
                enemy.update(dt)
        
        t = time.time()
        self.fleet_managers['my'].update(dt)
        self.fleet_managers['enemy'].update(dt)
        self.update_times['fleets'] = time.time() - t

        t = time.time()
        self.my_civ.update(dt)
        for enemy in self.enemies:
            enemy.civ.update(dt)
        self.update_times['civs'] = time.time() - t

        self.update_times['update'] = time.time() - ut
        

    def render(self):
        t = time.time()
        self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        if self.debug:
            for k,v in self.fleet_managers.items():
                for fleet in v.current_fleets:
                    fleet.debug_render(self.game.screen)

            gi = pygame.Surface(self.game.screen.get_size(), pygame.SRCALPHA)
            gi.fill((0,0,0,0))
            ff = list(self.flowfield.fields.values())[self.flowfielddebug]
            for y,gr in enumerate(ff.grid):
                for x,gc in enumerate(gr):
                    if gc:
                        p1 = V2((x + 0.5) * flowfield.GRIDSIZE, (y + 0.5) * flowfield.GRIDSIZE)
                        p2 = p1 + gc * flowfield.GRIDSIZE * 0.75
                        pygame.draw.line(gi, (0,0,255), p1.tuple(),p2.tuple())
                        pygame.draw.circle(gi, (0,0,255), p1.tuple(), 1)
            

            for y in range(len(self.objgrid.grid)):
                for x in range(len(self.objgrid.grid[0])):
                    x1 = x * self.objgrid.grid_size
                    y1 = y * self.objgrid.grid_size
                    pygame.draw.rect(gi, (0,255,0,150), (x1,y1,self.objgrid.grid_size+1, self.objgrid.grid_size+1), 1)
                    FONTS['tiny'].render_to(gi, (x1 + 2, y1 + 2), "%d" % len(self.objgrid.grid[y][x]), (128,255,128,180))

            self.game.screen.blit(gi, (0,0))

        for s in self.ui_group.sprites():
            if s.image is None:
                pass
                #print(s)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)
        if self.debug:
            self.enemy.render(self.game.screen)
            debug_render(self.game.screen, self)

        self.update_times['render'] = time.time() - t

        #FONTS['small'].render_to(self.game.screen, (5,game.RES[1] - 25), "%d" % self.time, (255,255,255,255))
        if self.debug:
            pass
            #print("\n".join(["%s:%.1f" % (a,b * 1000) for a,b in self.update_times.items()]))

        if game.DEV:
            FONTS['tiny'].render_to(self.game.screen, (game.RES[0] - 20, 20), "%d" % self.time, (128,255,128,180))


    def take_input(self, inp, event):
        if inp == "other" and game.DEV:
            if event.key == pygame.K_d:
                self.debug = not self.debug
            if event.key == pygame.K_1:
                self.game.game_speed_input = 0
            if event.key == pygame.K_0:
                self.game.game_speed_input = 1
            if event.key == pygame.K_f:
                self.flowfielddebug = (self.flowfielddebug + 1) % len(self.flowfield.fields)
        if inp == "menu": #TODO: pause menu
            pass

        return super().take_input(inp, event)
