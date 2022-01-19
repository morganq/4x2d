import random

import pygame
from colors import *
from helper import clamp
from planet import building as buildings
from productionorder import ProductionOrder
from stats import Stats
from upgrade.building_upgrades import (AddBuildingUpgrade,
                                       make_simple_stats_building)
from upgrade.upgrades import Upgrade, register_upgrade

V2 = pygame.math.Vector2

from aliens import (alien, alien3battleship, alien3bomber, alien3colonist,
                    alien3fighter)
from aliens.alien3battleship import Alien3Battleship
from aliens.alien3void import Alien3Void
from aliens.buildorder import *


@register_upgrade
class Alien3FighterProductionUpgrade1(Upgrade):
    name = "a3sfighter"
    resource_type = "iron"
    category = "ships"
    title = "Alien Fighter Production"
    description = "[^2] [Fighters] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien3'
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien3fighter", 2, 10)
        to.add_production(p)

@register_upgrade
class Alien3FighterProductionUpgrade2(Alien3FighterProductionUpgrade1):
    name = "a3sbomber"
    resource_type = "ice"
    category = "ships"
    title = "Alien Bomber Production"
    description = "[^2] [Bombers] Over 60 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien3'
    infinite = True
    alien_min_level = 4

    def apply(self, to):
        to.add_production(ProductionOrder("alien3bomber", 2, 60))

@register_upgrade
class Alien3FighterProductionUpgrade3(Alien3FighterProductionUpgrade1):
    name = "a3sbattleship"
    resource_type = "gas"    
    alien_min_level = 7

    def apply(self, to):
        if to.owning_civ.alien.difficulty > 1:
            to.add_production(ProductionOrder("alien3battleship", 1, 10))

@register_upgrade
class Alien3Tech1Upgrade(Upgrade):
    name = "a3tvoid"
    resource_type = "iron"
    category = "tech"
    title = "Alien Tech"
    description = "Grow Void"
    icon = "preciseassembly"
    stats = Stats()
    requires = None
    alien = True
    alien_name = 'alien3'
    infinite = True

    def apply(self, to):
        to.alien.grow_void()
        return super().apply(to)

@register_upgrade
class Alien3Tech1Upgrade2(Alien3Tech1Upgrade):
    name = "a3tice"
    resource_type = "ice"
    stats = Stats(gas_mining_rate=0.33)
    

@register_upgrade
class Alien3Tech1Upgrade3(Alien3Tech1Upgrade):
    name = "a3tgas"
    resource_type = "gas"

@register_upgrade
class Alien3EconUpgrade(AddBuildingUpgrade):
    name = "a3becon"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+33%] mining rate"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'alien3'
    building = make_simple_stats_building(stats=Stats(mining_rate=0.25), shape="voidecon")
    infinite = True

@register_upgrade
class Alien3EconUpgrade2(Alien3EconUpgrade):
    name = "a3bice"
    resource_type = "ice"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.65), shape="voidecon2")

@register_upgrade
class Alien3EconUpgrade3(Alien3EconUpgrade):
    name = "a3bgas"
    resource_type = "gas"   
    building = make_simple_stats_building(stats=Stats(top_mining_per_building=0.25), shape="voidecon2") 

class Alien3(alien.Alien):
    name = "alien3"
    title = "VOID KEEPERS"
    ATTACK_DURATION = 15
    DEFEND_DURATION = 15
    EXPAND_NUM_NEAREST = 2
    EXPAND_DURATION = 12
    COLOR = PICO_ORANGE

    quotes = [
        "\"Has it called you here? Will you face the void?\""
    ]

    tips = [
        ("assets/alieninfo-void.png", "VOID KEEPERS generate VOID FIELDS around their planets, which grant shields and speed to their ships."),
        ("assets/alieninfo-stealth.png", "KEEPERS' STEALTH BOMBER is invisible within VOID FIELDS."),
        ("assets/alieninfo-mothership.png", "KEEPERS' MOTHERSHIP produces its own VOID FIELDS for attacking fleets.")
    ]    

    def __init__(self, scene, civ):
        super().__init__(scene, civ)
        self.planet_void = {}
        self.ship_void = {}

    def get_build_order_steps(self):
        bo = [
            BOResearch(0,"a3sfighter"),
            BOExpand(10, BOExpand.TARGET_TYPE_MIDDLE),
            BOResearch(20,"a3becon"),
            BOResearch(40, "a3bice", "a3becon"),
            BOResearch(50,"a3sbomber", "a3sfighter", target_type=BOResearch.TARGET_TYPE_RANDOM),
            BOExpand(50, BOExpand.TARGET_TYPE_MIDDLE),
            BOResearch(70,"a3sbomber", "a3sfighter", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(70,"a3tvoid"),
            BOResearch(80,"a3tvoid"),
            BOResearch(90,"a3sfighter", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(100,"a3sbattleship", "a3sbomber", target_type=BOResearch.TARGET_TYPE_RANDOM),
            BOAttack(110, BOAttack.ATTACK_TYPE_OUTLYING, 0.33),
        ]
        if self.difficulty >= 3:
            bo.append(BOAttack(115, BOAttack.ATTACK_TYPE_RANDOM, 0.33))
        if self.difficulty >= 5:
            bo.append(BOAttack(120, BOAttack.ATTACK_TYPE_RANDOM, 0.33))
        return bo

    def set_difficulty(self, difficulty):
        #if difficulty > 1:
        #    self.civ.base_stats['void'] = 1
        super().set_difficulty(difficulty)
        #self.EXPAND_DURATION = max(30 - (difficulty * 2), 10)

    def update(self, dt):
        if self.difficulty > 1:
            # Create void for planets
            for planet in self.scene.get_civ_planets(self.civ):
                if planet not in self.planet_void:
                    void = Alien3Void(self.scene, planet, planet.get_radius() + 10, self.civ.color)
                    self.planet_void[planet] = void
                    self.scene.game_group.add(void)

            # Destroy void for destroyed planets
            for planet in list(self.planet_void.keys()):
                if planet.owning_civ != self.civ:
                    self.planet_void[planet].kill()
                    del self.planet_void[planet]

            # Create void for ships
            for ship in self.scene.get_civ_ships(self.civ):
                if isinstance(ship, Alien3Battleship) and ship not in self.ship_void:
                    void = Alien3Void(self.scene, ship, 15)
                    self.ship_void[ship] = void
                    self.scene.game_group.add(void)

            # Destroy void for dead ships
            for ship in list(self.ship_void.keys()):
                if ship.owning_civ != self.civ or not ship.is_alive():
                    self.ship_void[ship].kill()
                    del self.ship_void[ship]                    

        self.civ.voids = list(self.planet_void.values()) + list(self.ship_void.values())
        return super().update(dt)

    def grow_void(self):
        for void in self.planet_void.values():
            void.grow()

    def get_attacking_ships(self):
        return ['alien3fighter', 'alien3bomber', 'alien3battleship']

    def get_colonist(self):
        return 'alien3colonist'

alien.ALIENS['alien3'] = Alien3
