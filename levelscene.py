from pathfinder import Pathfinder
from spaceobject import SpaceObject
import simplesprite
import sys
import traceback
import random

import pygame

import game
import levelstates
import scene
import states
from asteroid import Asteroid
from background import Background
from civ import PlayerCiv, Civ
from meter import Meter
from button import Button
from text import Text, FONTS
from colors import *
from economy import RESOURCES, Resources, RESOURCE_COLORS
from planet.planet import Planet
from resources import resource_path
from ships.ship import Ship
import fleet
from v2 import V2
from aliens.basicalien import BasicAlien
from debug import debug_render


class LevelScene(scene.Scene):
    def __init__(self, game, options=None):
        scene.Scene.__init__(self, game)
        self.options = options
        self.animation_timer = 0
        self.my_civ = PlayerCiv(self)
        self.enemy = BasicAlien(self, Civ(self))

        self.paused = False
        self.game_speed = 1.0
        self.time = 0
        self.debug = False
        self._score = 0

    @property
    def score(self):
        return self._score

    @score.setter
    def score(self, value):
        self._score = value
        self.score_text.set_text("%d" % value)

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
            for obj in self.get_objects():
                delta = (obj.pos - pos).sqr_magnitude()
                if delta < dist:
                    dist = delta
            if dist <= 30 ** 2:
                pos = None
                continue

            
        return pos

    def give_building(self, planet, building):
        planet.add_building(building)
        planet.owning_civ.researched_upgrade_names.add(building)

    def load(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()

        self.background_group.add(Background(V2(0,0)))

        # Me
        homeworld = Planet(self, V2(60, game.RES[1] - 40), 7, Resources(100, 0, 0))
        homeworld.change_owner(self.my_civ)
        homeworld.population = 4
        homeworld.ships['fighter'] = 2
        self.game_group.add(homeworld)

        # Alien
        p = Planet(self, V2(420, 60), 5, Resources(70, 20, 10))
        p.change_owner(self.enemy.civ)
        p.population = 5
        p.ships['alien-fighter'] = 2
        self.give_building(p, "alienhomedefense")
        self.game_group.add(p)
        num_planets = 2

        # TODO: Planet resources more constrained
        while num_planets < 15:
            pos = V2(random.randint(30, game.RES[0] - 30), random.randint(30, game.RES[1] - 30))
            
            near_button = pygame.Rect(game.RES[0] / 2 - 100, game.RES[1] - 60, 200, 60)
            if near_button.collidepoint(*pos.tuple()):
                continue

            near_meters = pygame.Rect(0, 0, 250, 60)
            if near_meters.collidepoint(*pos.tuple()):
                continue            
            
            dist = 999999
            for obj in self.get_objects():
                delta = (obj.pos - pos).sqr_magnitude()
                if delta < dist:
                    dist = delta
            if dist > 70 ** 2:
                if pos.x /2 + (game.RES[1] - pos.y) < game.RES[1] - 100:
                    size = random.randint(4,7)
                    if random.random() > 0.5:
                        pr = Resources(100, 0, 0)
                    else:
                        size -= 1
                        iron = random.randint(7,10)
                        pr = Resources(iron * 10, (10 - iron) * 10, 0)
                else:
                    size = random.randint(3, 7)
                    resources = {'a':0, 'b':0, 'c':0}
                    # One resource
                    ra = random.random()
                    if ra > 0.75:
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
                    if rb > 0.6:
                        pr = Resources(resources['a'] * 10, resources['b'] * 10, resources['c'] * 10)
                        size += 1
                    elif rb > 0.25:
                        pr = Resources(resources['b'] * 10, resources['a'] * 10, resources['c'] * 10)
                    else:
                        pr = Resources(resources['c'] * 10, resources['b'] * 10, resources['a'] * 10)
                        size -= 1
                self.game_group.add(Planet(self, pos, size, pr))
                num_planets += 1

        for i in range(20):
            pos = self.random_object_pos()
            self.game_group.add(Asteroid(self, pos, Resources(random.randint(20,80), random.randint(0,30), random.randint(0,10))))

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

        self.help_button = Button(V2(2, 48), "Help", "small", self.on_click_help)
        self.ui_group.add(self.help_button)

        self.score_label = Text("- Score -", "small", V2(game.RES[0] - 2, 2), PICO_BLUE)
        self.score_label.offset = (1, 0)
        self.score_label._recalc_rect()        
        self.ui_group.add(self.score_label)

        self.score_text = Text("0", "small", V2(game.RES[0] - 2, 12), PICO_BLUE)
        self.score_text.offset = (1, 0)
        self.score_text._recalc_rect()
        self.ui_group.add(self.score_text)

        self.my_civ.resources.set_resource("iron", 30)

        if self.options == "iron":
            self.my_civ.resources.set_resource("iron", 1150)

        if self.options == "ice":
            self.my_civ.resources.set_resource("ice", 1150)

        if self.options == "gas":
            self.my_civ.resources.set_resource("gas", 1150)    

        if self.options == "buildings":
            homeworld.add_building("econ1")
            homeworld.add_building("econ2a")
            homeworld.add_building("econ2b")
            homeworld.add_building("econ3")

        if self.options == "surround":
            for planet in self.get_civ_planets(None):
                planet.change_owner(self.enemy.civ)
                #planet.add_ship("alien-fighter")
                #planet.add_ship("alien-fighter")
                #self.my_civ.resources.set_resource("iron", 50)
                #self.my_civ.resources.set_resource("ice", 50)
                self.my_civ.resources.set_resource("gas", 50)

        if self.options == "fighters":
            for i in range(20):
                homeworld.add_ship("fighter")

        if self.options == "battleship":
            from ships.alienbattleship import AlienBattleship
            bs = AlienBattleship(self, V2(150, 250), self.enemy.civ)
            bs.target = homeworld
            self.game_group.add(bs)

        if self.options == "score":
            homeworld.change_owner(self.enemy.civ)

        if self.options == "rich":
            self.my_civ.resources.set_resource("iron", 1150)
            self.my_civ.resources.set_resource("ice", 1150)
            self.my_civ.resources.set_resource("gas", 1150)    

        if self.options == "hangars":
            self.my_civ.researched_upgrade_names.add("hangar2a")
            self.my_civ.researched_upgrade_names.add("hangar2b")
            homeworld.add_building("hangar2a")
            homeworld.add_building("hangar2b")
            self.my_civ.resources.set_resource("ice", 1150)

        self.pathfinder = Pathfinder(self)
        self.pathfinder.generate_grid()
        self.fleet_managers = {
            'my':fleet.FleetManager(self, self.my_civ),
            'enemy':fleet.FleetManager(self, self.enemy.civ)
        }

    def on_click_help(self):
        self.sm.transition(levelstates.HelpState(self))

    def on_click_upgrade(self):
        self.sm.transition(levelstates.UpgradeState(self))

    def on_civ_resource_change(self, res_type, val):
        while self.my_civ.resources.data[res_type] >= self.my_civ.upgrade_limits.data[res_type]:
            self.my_civ.upgrades_stocked.append(res_type)
            self.my_civ.resources.data[res_type] -= self.my_civ.upgrade_limits.data[res_type]
            self.my_civ.upgrade_limits.data[res_type] += 25
        self.meters[res_type].max_value = self.my_civ.upgrade_limits.data[res_type]
        self.meters[res_type].value = self.my_civ.resources.data[res_type]

    def get_objects(self):
        return [s for s in self.game_group.sprites() if isinstance(s,SpaceObject)]

    def get_planets(self):
        return [s for s in self.game_group.sprites() if isinstance(s,Planet)]

    def get_civ_planets(self, civ):
        return [s for s in self.game_group.sprites() if isinstance(s,Planet) and s.owning_civ == civ]

    def get_ships(self):
        return [s for s in self.game_group.sprites() if isinstance(s,Ship)]

    def get_my_ships(self):
        return [s for s in self.game_group.sprites() if isinstance(s,Ship) and s.owning_civ == civ]

    def get_enemy_ships(self, civ):
        return [s for s in self.game_group.sprites() if isinstance(s,Ship) and s.owning_civ != civ]

    def get_enemy_objects(self, civ):
        return [s for s in self.game_group.sprites() if (isinstance(s,Ship) or isinstance(s,Planet)) and s.owning_civ != civ]

    def get_civ_ships(self, civ):
        return [s for s in self.game_group.sprites() if isinstance(s,Ship) and s.owning_civ == civ]        

    def get_hazards(self):
        return self.get_planets()

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
        dt *= self.game_speed
        if self.paused:
            return        
        self.time += dt
        scene.Scene.update(self, dt)

        # Detect defeat
        if not self.get_civ_planets(self.my_civ):
            self.paused = True
            self.sm.transition(levelstates.GameOverState(self))
        
        # Detect victory
        if not self.get_civ_planets(self.enemy.civ):
            self.paused = True
            self.sm.transition(levelstates.VictoryState(self))

        for sprite in self.game_group.sprites():
            sprite.update(dt)

        for sprite in self.ui_group.sprites():
            sprite.update(dt)

        colliders = [s for s in self.game_group.sprites() if s.collidable]
        lc = len(colliders)
        for i in range(lc):
            for j in range(i + 1, lc):
                d = colliders[i].pos - colliders[j].pos
                if d.sqr_magnitude() <= (colliders[i].collision_radius + colliders[j].collision_radius) ** 2:
                    colliders[i].collide(colliders[j])
                    colliders[j].collide(colliders[i])

        if len(self.my_civ.upgrades_stocked) > 0:
            r = self.my_civ.upgrades_stocked[0]
            text = "UPGRADE - %s" % r.upper()
            if self.upgrade_button.visible == False or self.upgrade_button.text != text:
                self.upgrade_button.visible = True
                self.upgrade_button.text = text
                self.upgrade_button.color = RESOURCE_COLORS[r]
                self.upgrade_button._generate_image()
        else:
            if self.upgrade_button.visible:
                self.upgrade_button.visible = False

        for res_type in self.my_civ.resources.data.keys():
            num = len([u for u in self.my_civ.upgrades_stocked if u == res_type])
            if num > 0:
                self.upgrade_texts[res_type].set_text("%d upgrade%s available!" % (num, "s" if num > 1 else ""))
            else:
                self.upgrade_texts[res_type].set_text("")

        self.enemy.update(dt)
        
        self.fleet_managers['my'].update(dt)
        self.fleet_managers['enemy'].update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.update_layers()
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        if self.debug:
            for k,v in self.fleet_managers.items():
                for fleet in v.current_fleets:
                    fleet.debug_render(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)
        if self.debug:
            self.enemy.render(self.game.screen)
            debug_render(self.game.screen, self)

        #FONTS['small'].render_to(self.game.screen, (5,game.RES[1] - 25), "%d" % self.time, (255,255,255,255))            


    def take_input(self, inp, event):
        if inp == "other":
            if event.key == pygame.K_d:
                self.debug = not self.debug
            if event.key == pygame.K_1:
                self.game_speed = 1.0
            if event.key == pygame.K_0:
                self.game_speed = 10.0
        return super().take_input(inp, event)