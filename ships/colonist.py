import random

import helper
import sound
from colors import *
from explosion import Explosion
from icontext import IconText
from particle import Particle
from planet import planet
from text import Text
from upgrade.upgrades import UPGRADE_CLASSES
import pygame
V2 = pygame.math.Vector2

from ships.all_ships import register_ship

from .ship import ATMO_DISTANCE, STATE_WAITING, THRUST_PARTICLE_RATE, Ship

ATOMIC_BOMB_RANGE = 20

@register_ship
class Colonist(Ship):
    HEALTHBAR_SIZE = (16,2)
    BASE_HEALTH = 30
    SHIP_NAME = "colonist"
    
    def __init__(self, scene, pos, owning_civ):
        Ship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/colonist.png", 12)
        self.collision_radius = 4
        self.population = 0
    
    def set_pop(self, pop):
        self.population = pop
        self.num_label = Text(str(self.population), "small", self.pos + V2(7, -7), PICO_WHITE,shadow=PICO_BLACK)
        self.scene.ui_group.add(self.num_label)

    def can_land(self, other):
        return (
            other == self.effective_target and
            isinstance(other, planet. Planet) and
            (other.owning_civ == None or other.owning_civ == self.owning_civ) and
            other.alive()
        )

    def collide(self, other):
        if self.can_land(other):
            self.kill()
            if other.owning_civ != self.owning_civ:
                other.change_owner(self.owning_civ)
                if self.get_stat("colonize_random_building"):
                    available_upgrades = [
                        u for u in UPGRADE_CLASSES.values()
                        if u.alien == False and
                        len(u.family['parents']) == 0 and
                        u.category == "buildings" and
                        u.resource_type == "iron"
                    ]
                    u = random.choice(available_upgrades)
                    u().apply(other)  
                    self.owning_civ.researched_upgrade_names.add(u.name)       

                self.colonized(other)
                if self.origin:
                    self.origin.emitted_ship_colonized(self, other)
                self.owning_civ.housing_colonized = True                

            other.population += self.population

            other.needs_panel_update = True
        

    def colonized(self, planet):
        mods = self.scene.game.run_info.get_current_level_galaxy()['mods']
        if mods and mods[0] == 'reflector':
            planet.add_building(UPGRADE_CLASSES['b_defense1'])
        if self.get_stat("terraform"):
            if planet.resources.iron > 0:
                val = int(planet.resources.iron * 0.3)
                planet.resources.iron -= val
                if random.random() > 0.5:
                    planet.resources.ice += val
                else:
                    planet.resources.gas += val
                planet.regenerate_art()
        if self.owning_civ.is_player:
            sound.play("goodcapture")
        else:
            sound.play("badcapture")            


    def update(self, dt):
        if self.population <= 0:
            self.kill()
        super().update(dt)
        self.num_label.pos = self.pos + V2(7, -7)

    def on_warp(self):
        if random.random() < self.get_stat("warp_drive_pop_chance"):
            self.population += 3
            if self.owning_civ and self.owning_civ.is_player:
                it = IconText(self.pos, "assets/i-pop.png", "+3", PICO_GREEN)
                it.pos = self.pos + V2(0, -10) - V2(it.width, it.height) * 0.5
                self.num_label.set_text(str(self.population))
                self.scene.ui_group.add(it)
        return super().on_warp()

    def kill(self):
        if self.health <=0 and self.get_stat("atomic_bomb"):
            range_adjust = 0.75 + self.population * 0.25
            enemy_objs = self.scene.get_enemy_objects(self.owning_civ)
            near_enemies = helper.all_nearby(self.pos, enemy_objs, ATOMIC_BOMB_RANGE * range_adjust)
            for enemy in near_enemies:
                enemy.take_damage(self.population * 5)
            e = Explosion(self.pos, [PICO_GREEN, PICO_WHITE, PICO_GREEN, PICO_DARKGREEN], 0.75, ATOMIC_BOMB_RANGE * range_adjust, lambda x:helper.clamp(x * 3,0,1))
            self.scene.game_group.add(e)
            
        self.num_label.kill()
        return super().kill()

    def state_cruising(self, dt):
        delta = self.effective_target.pos - self.pos
        if isinstance(self.effective_target, planet.Planet):
            if (delta.length() - self.effective_target.radius - ATMO_DISTANCE) <= 0:
                if not self.can_land(self.effective_target):
                    self.set_state(STATE_WAITING)
                    return        
        return super().state_cruising(dt)
