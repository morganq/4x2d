import json
import random
import sys
import time
import traceback
from collections import defaultdict

import pygame

import aliens
import bullet
import fleet
import fleetdiagram
import flowfield
import funnotification
import game
import levelcontroller
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
from elements import flash, shake
from explosion import Explosion
from hazard import Hazard
from helper import all_nearby, get_nearest
from levelbackground import LevelBackground
from line import AssetLine, Line
from meter import Meter
from objgrid import ObjGrid
from planet.planet import Planet
from resources import resource_path
from ships.ship import Ship
from spaceobject import SpaceObject
from text import FONTS, Text, render_multiline_to
from upgrade.upgradeicon import UpgradeIcon
from upgrade.upgrades import UPGRADE_CLASSES
import pygame
V2 = pygame.math.Vector2

TICK_TIME = 0.05

class LevelSceneBase(scene.Scene):
    def __init__(self, game, levelfile):
        scene.Scene.__init__(self, game)
        self.levelfile = levelfile
        self.options = ""
        self.paused = False
        self.cinematic = False
        self.game_speed = 1.0
        self.time = 0
        self.debug = False
        self._score = 0
        self.is_tutorial = False
        self.update_times = defaultdict(lambda:0)

        self.update_remainder_time = 0
        self.level_controller = None
        self.shake_sprite = None

    def random_object_pos(self):
        pos = None
        while pos is None:
            pos = V2(random.randint(30, game.RES[0] - 30), random.randint(30, game.RES[1] - 30))
            pos += self.game.game_offset

            dist = 999999
            for obj in self.get_objects_initial():
                delta = (obj.pos - pos).length_squared()
                if delta < dist:
                    dist = delta
            if dist <= 30 ** 2:
                pos = None
                continue

            
        return pos

    def give_building(self, planet, upgrade):
        planet.add_building(upgrade)
        planet.owning_civ.researched_upgrade_names.add(upgrade.name)

    def create_layers(self):
        self.objgrid = ObjGrid(self.game.game_resolution.x, self.game.game_resolution.y, 50)
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.particle_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.LayeredDirty()

        self.background = LevelBackground(V2(0,0), self.game.game_resolution)
        self.background_group.add(self.background)
        self.fleet_diagram = fleetdiagram.FleetDiagram(V2(0,0), self)
        self.game_group.add(self.fleet_diagram)        

    def add_extra_spaceobjects(self):
        print("add space objects")
        num_planets = len(self.get_planets())

        max_planets = min(int(self.difficulty / 1.5 + 7), 16)

        if self.options == "flowfield":
            max_planets = 25

        separation = 70
        # TODO: Planet resources more constrained
        while num_planets < max_planets:
            avg_pos = sum([p.pos for p in self.get_planets()], V2(0,0)) / num_planets
            pos = V2(random.randint(30, game.RES[0] - 30), random.randint(30, game.RES[1] - 30))
            pos += self.game.game_offset

            # If we're most of the way through creating planets, and we're on the wrong side of the avg, flip it.
            if num_planets >= max_planets * 1 / 3:
                if ((avg_pos.x < self.game.game_resolution.x / 2 and pos.x < self.game.game_resolution.x /2) or
                    (avg_pos.x > self.game.game_resolution.x / 2 and pos.x > self.game.game_resolution.x /2)):
                    pos = V2(self.game.game_resolution.x - pos.x, pos.y)
            
            #near_button = pygame.Rect(self.game_resolution.x / 2 - 100, self.game_resolution.y - 60, 200, 60)
            #if near_button.collidepoint(*pos):
            #    continue

            #near_meters = pygame.Rect(0, 0, 250, 60)
            #if near_meters.collidepoint(*pos):
            #    continue            
            
            dist = 999999
            for obj in self.get_objects_initial():
                delta = (obj.pos - pos).length_squared()
                if delta < dist:
                    dist = delta
            if dist > separation ** 2:
                size = random.randint(2, 6)
                resources = {'a':0, 'b':0, 'c':0}
                # One resource
                ra = random.random()
                if ra > 0.66:
                    resources['a'] = 10
                # Two resource
                elif ra > 0.2:
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
                    size -= 1
                else:
                    pr = Resources(resources['c'] * 10, resources['b'] * 10, resources['a'] * 10)
                    size -= 1
                self.game_group.add(Planet(self, pos, size, pr))
                num_planets += 1
            else:
                separation -= 1

        if self.difficulty < 9:
            for i in range(random.randint(15,20) - int(self.difficulty / 3)):
                pos = self.random_object_pos()
                self.game_group.add(Asteroid(self, pos, Resources(random.randint(20,80), random.randint(0,30), random.randint(0,10))))  

    def add_particle(self, particle):
        if len(self.particle_group.sprites()) > 50:
            self.particle_group.sprites()[0].kill()
        self.particle_group.add(particle)

    def get_fleet_manager(self, civ):
        return None

    def get_objects_initial(self):
        return [s for s in self.game_group.sprites() if isinstance(s,SpaceObject)]

    def get_objects(self):
        return self.objgrid.all_objects

    def get_objects_in_range(self, pos, range):
        return self.objgrid.get_objects_near(pos, range)

    def get_planets(self):
        return [s for s in self.game_group.sprites() if isinstance(s,Planet)]

    def get_planets_in_range(self, pos, range):
        return [o for o in self.objgrid.get_objects_near(pos, range) if isinstance(o,Planet)]

    def get_civ_planets(self, civ, skip_objgrid = False):
        if skip_objgrid:
            return [s for s in self.get_objects_initial() if isinstance(s,Planet) and s.owning_civ == civ] 
        return [s for s in self.get_objects() if isinstance(s,Planet) and s.owning_civ == civ]

    def get_enemy_planets(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Planet) and s.owning_civ and s.owning_civ != civ]        

    def get_enemy_civs(self, civ):
        return []

    def get_special_enemies_in_range(self, civ, pos, range):
        return [s for s in self.get_objects_in_range(pos,range) if isinstance(s,bossmothership.BossMothership) and s.owning_civ != civ]

    def get_ships(self):
        return [s for s in self.get_objects() if isinstance(s,Ship)]
    
    def get_my_ships(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ == civ]

    def get_my_ships_in_range(self, civ, pos, range):
        return [s for s in self.get_objects_in_range(pos,range) if isinstance(s,Ship) and s.owning_civ == civ]

    def get_enemy_ships(self, civ):
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ != civ]

    def get_enemy_ships_in_range(self, civ, pos, range):
        return [s for s in self.get_objects_in_range(pos,range) if isinstance(s,Ship) and s.owning_civ != civ]

    def get_enemy_objects_in_range(self, civ, pos, range):
        return [
            s for s in self.get_objects_in_range(pos, range)
            if (
                hasattr(s, "owning_civ") and
                s.owning_civ and s.owning_civ != civ and
                not isinstance(s, bullet.Bullet)
            )
        ]

    def get_enemy_objects(self, civ):
        return [s for s in self.get_objects() if (isinstance(s,Ship) or isinstance(s,Planet)) and s.owning_civ and s.owning_civ != civ]

    def get_civ_ships(self, civ, skip_objgrid = False):
        if skip_objgrid:
            return [s for s in self.get_objects_initial() if isinstance(s,Ship) and s.owning_civ == civ]
        return [s for s in self.get_objects() if isinstance(s,Ship) and s.owning_civ == civ]        

    def get_hazards(self):
        return [s for s in self.get_objects() if isinstance(s, Hazard)]

    def get_asteroids(self):
        return [s for s in self.get_objects() if isinstance(s, Asteroid)]

    def get_starting_state(self):
        return levelstates.BeginState(self)

    def initialize_state(self):
        self.sm = states.Machine(self.get_starting_state())

    def update_layers(self):
        pass

    def start(self):
        self.load()
        self.initialize_state()
        #sound.play_music('game')  

    def update(self, dt):
        dt = min(dt,0.1)
        if not self.cinematic:
            self.game_speed = round((self.game.game_speed_input * 3) + 1)
        # This is correct way to do things, but we need to optimize more for this to work
        #game_dt = dt * self.game_speed        
        #self.update_remainder_time += dt
        #num_updates = int(self.update_remainder_time / TICK_TIME)
        #for i in range(num_updates):
        #    self.update_game(TICK_TIME * self.game_speed)
        #    self.update_remainder_time -= TICK_TIME

        self.update_game(dt * self.game_speed, dt)
        self.update_ui(dt)

    def update_ui(self, dt):
        for sprite in self.ui_group.sprites():
            sprite.update(dt)        

        if self.radar:
            for spr in self.game_group.sprites():
                if isinstance(spr, Planet) or isinstance(spr, Asteroid):
                    delta = spr.pos - self.radar.pos
                    if delta.length_squared() < self.radar.size ** 2:
                        if not spr.visible:
                            flash.flash_sprite(spr)
                            #shake.shake(self, spr.pos, 30)
                        spr.visible = True
                    else:
                        spr.visible = False
            if self.radar.time > 1.25:
                self.radar.kill()
                self.radar = None           

    def update_game(self, dt, base_dt):
        ut = time.time()
        self.update_times = defaultdict(lambda:0)
        if self.paused:
            self.sm.state.paused_update(base_dt)
            return        

        self.time += dt

        if self.level_controller:
            self.level_controller.update(dt)
            
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

        self.update_game_objects(dt)
        self.update_collisions(dt)

        self.flowfield.update(dt)

    def update_collisions(self, dt):
        #t = time.time()
        # Collisions
        colliders = [s for s in self.get_objects() if s.collidable and not s.stationary]
        lc = len(colliders)
        #print(lc, "colliders")
        checked = set()
        for first in colliders:
            MAX_COLLISION_RANGE = 30 # Arbitrary guess...
            near = self.objgrid.get_objects_near(first.pos, MAX_COLLISION_RANGE) 
            for second in near:
                if second in checked: # Don't double collide
                    continue
                if second == first:
                    continue
                if first.stationary and second.stationary:
                    continue
                d = first.pos - second.pos
                if d.length_squared() <= (first.collision_radius + second.collision_radius) ** 2:
                    first.collide(second)
                    second.collide(first)

            checked.add(first)

        #elapsed = time.time() - t
        #self.update_times["collisions"] = elapsed

    def update_particles(self, dt):
        for s in self.particle_group.sprites():
            s.update(dt)

    def update_game_objects(self, dt):
        for sprite in self.game_group.sprites():
            sprite.update(dt)

        if self.shake_sprite:
            self.shake_sprite.update(dt)  
            if self.shake_sprite.time > self.shake_sprite.end_time:
                self.shake_sprite = None

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
        self.particle_group.draw(self.game.screen)
        if self.shake_sprite:
            self.shake_sprite.render(self.game.screen)

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
                            pygame.draw.line(gi, (0,0,255), p1,p2)
                            pygame.draw.circle(gi, (0,0,255), p1, 1)
                        else:
                            pygame.draw.circle(gi, (255,0,255), p1, 3, 1)
            
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
            surf = pygame.Surface(res, pygame.SRCALPHA)
            pygame.draw.rect(surf, PICO_DARKBLUE, (0,0,res.x,40), 0)
            pygame.draw.rect(surf, PICO_DARKBLUE, (0,res.y-40,res.x,40), 0)
            #surf.set_alpha(160)
            self.game.screen.blit(surf, (0,0))

        return None

    def update_run_stats(self):
        self.game.run_info.time_taken += self.time
        self.game.run_info.ships_lost += self.player_civ.ships_lost

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
            if event.key == pygame.K_g:
                self.flowfielddebugstage = (self.flowfielddebugstage + 1) % 4
            if event.key == pygame.K_h:
                self.flowfielddebug = len(self.flowfield.fields) - 1
        if inp == "menu": #TODO: pause menu
            pass

        return super().take_input(inp, event)    
