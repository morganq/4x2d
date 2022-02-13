import random

import helper
import pygame
from colors import *
from helper import clamp
from planet import building as buildings
from productionorder import ProductionOrder
from resources import resource_path
from spritebase import SpriteBase
from stats import Stats
from upgrade.building_upgrades import (AddBuildingUpgrade,
                                       make_simple_stats_building)
from upgrade.upgrades import Upgrade, register_upgrade

V2 = pygame.math.Vector2

from aliens import (alien, alien2battleship, alien2colonist, alien2controlship,
                    alien2fighter)
from aliens.alien2battleship import Alien2Battleship
from aliens.buildorder import *


@register_upgrade
class Alien2FighterProductionUpgrade1(Upgrade):
    name = "alien2fighters"
    resource_type = "iron"
    category = "ships"
    title = "Alien Fighter Production"
    description = "[^2] [Fighters] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien2'
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien2fighter", 2, 10)
        to.add_production(p)

@register_upgrade
class Alien2FighterProductionUpgrade2(Alien2FighterProductionUpgrade1):
    name = "alien2controlship"
    resource_type = "ice"
    category = "ships"
    title = "Alien Control Ship Production"
    description = "[^1] [Control Ship] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien2'
    infinite = True
    alien_min_level = 3

    def apply(self, to):
        p = ProductionOrder("alien2controlship", 1, 10)
        to.add_production(p)

@register_upgrade
class Alien2FighterProductionUpgrade3(Alien2FighterProductionUpgrade1):
    name = "alien2battleship"
    resource_type = "gas"    
    alien_min_level = 6

    def apply(self, to):
        if to.owning_civ.alien.difficulty <= 1:
            return
        found_ship = None
        for ship in to.scene.get_civ_ships(to.owning_civ):
            if isinstance(ship, Alien2Battleship):
                found_ship = ship
                break

        if found_ship and not found_ship.constructed:
            found_ship.frame += 1
            if found_ship.frame == 2:
                found_ship.constructed = True
                target = random.choice(to.scene.get_civ_planets(to.scene.player_civ))
                found_ship.set_target(target)
        else:
            pos = to.pos + helper.random_angle() * (to.radius + 20)
            ship = Alien2Battleship(to.scene, pos, to.owning_civ)
            ship.frame = 0
            ship.constructed = False
            to.scene.game_group.add(ship)

@register_upgrade
class Alien2Tech1Upgrade(Upgrade):
    name = "alien2techspeed"
    resource_type = "iron"
    category = "tech"
    title = "Alien Tech"
    description = "[Alien Fighters] gain [^+33%] speed"
    icon = "preciseassembly"
    stats = Stats(ship_speed_mul=0.33)
    requires = None
    alien = True
    alien_name = 'alien2'
    infinite = True

@register_upgrade
class Alien2Tech1Upgrade2(Alien2Tech1Upgrade):
    name = "alien2techcontrol"
    resource_type = "ice"
    stats = Stats(alien_control_mul=-0.125)
    

@register_upgrade
class Alien2Tech1Upgrade3(Alien2Tech1Upgrade):
    name = "alien2techrof3"
    resource_type = "gas"

@register_upgrade
class Alien2HomeDefenseUpgrade(AddBuildingUpgrade):
    name = "alien2homedefense"
    resource_type = "iron"
    category = "buildings"
    title = "Alien Home Defense"
    description = "Planet fires missiles at nearby enemy ships"
    icon = "mining"
    family = {}
    building = buildings.AlienHomeDefenseBuilding
    requires = lambda x: False
    alien = True
    alien_name = 'alien2'

@register_upgrade
class Alien2EconUpgrade(AddBuildingUpgrade):
    name = "alien2econrate"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+33%] mining rate"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'alien2'
    building = make_simple_stats_building(stats=Stats(mining_rate=0.33), shape="networkecon")
    infinite = True

@register_upgrade
class Alien2EconUpgrade2(Alien2EconUpgrade):
    name = "alien2econpop2"
    resource_type = "ice"
    building = make_simple_stats_building(stats=Stats(mining_gas_per_iron=0.5), shape="networkecon2")

@register_upgrade
class Alien2EconUpgrade3(Alien2EconUpgrade):
    name = "alien2econpop3"
    resource_type = "gas"    


class Alien2CurseIndicator(SpriteBase):
    def __init__(self, planet):
        super().__init__(planet.pos)
        self.planet = planet
        self._offset = (0.5, 0.5)
        self._generate_image()

    def _generate_image(self):
        d = 10
        self._width = (self.planet.radius + d + 6) * 2
        self._height = self._width
        cancel = pygame.image.load(resource_path("assets/cancel.png")).convert_alpha()
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        c = V2(self._width // 2, self._height // 2)
        for i in range(8):
            theta = i * 3.14159 / 4
            p1 = helper.from_angle(theta) * (self.planet.radius + d)
            p2 = helper.from_angle(theta + 0.05) * (self.planet.radius + d + 5)
            p3 = helper.from_angle(theta) * (self.planet.radius + d + 4)
            p4 = helper.from_angle(theta - 0.05) * (self.planet.radius + d + 5)
            pts = [(p + c) for p in [p1,p2,p3,p4]]
            pygame.draw.polygon(self.image, PICO_RED, pts, 0)

        self.image.blit(cancel, (c - V2(4,4)))

        self._recalc_rect()


class Alien2(alien.Alien):
    name = "alien2"
    title = "THE NETWORK"
    ATTACK_DURATION = 15
    DEFEND_DURATION = 3
    EXPAND_NUM_NEAREST = 1
    EXPAND_DURATION = 10
    COLOR = PICO_YELLOW

    quotes = [
    ]

    tips = [
        ("assets/alieninfo-intimidate.png", "THE NETWORK can INTIMIDATE a planet, preventing new buildings or ships from being made there."),
        ("assets/alieninfo-worm.png", "NETWORK'S SUPERVISOR ships can HACK and take control of your ships unless you destroy them quickly."),
        ("assets/alieninfo-destroyer.png", "NETWORK'S DESTROYERS take a long time to build, but can defeat a whole fleet in combat.")
    ]    

    @classmethod
    def get_quote(kls):
        return "\"Factory Default Signal. Change Me!\""

    def __init__(self, scene, civ):
        super().__init__(scene, civ)
        self.attack_from = None
        self.attack_to = None
        self.pick_new_target_time = 0
        self.curse = None

    def get_build_order_steps(self):
        bo = [
            BOResearch(5,"alien2homedefense", target_type=BOResearch.TARGET_TYPE_LACKING_ASSET),
            BOResearch(10,"alien2fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(20,"alien2econrate"),
            BOExpand(35),
            BOExpand(35, target_type=BOExpand.TARGET_TYPE_NEAR_ENEMY),
            BOResearch(36,"alien2controlship", "alien2fighters"),
            BOResearch(70,"alien2homedefense", target_type=BOResearch.TARGET_TYPE_LACKING_ASSET),
            BOResearch(70,"alien2fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOExpand(70),
            BOResearch(90,"alien2fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(90,"alien2homedefense", target_type=BOResearch.TARGET_TYPE_LACKING_ASSET),
            BOResearch(90,"alien2controlship", "alien2fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(90,"alien2battleship", "alien2controlship", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOAttack(120, BOAttack.ATTACK_TYPE_OUTLYING),
            BOResearch(120,"alien2homedefense", target_type=BOResearch.TARGET_TYPE_LACKING_ASSET),
            BOResearch(120, "alien2techspeed"),
            BOResearch(130, "alien2techspeed"),            
            BOResearch(140,"alien2homedefense", target_type=BOResearch.TARGET_TYPE_LACKING_ASSET),
            BOAttack(160, BOAttack.ATTACK_TYPE_OUTLYING),
            BOResearch(160,"alien2battleship", "alien2controlship", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
        ]
        if self.difficulty >= 3:
            bo.append(BOAttack(162, BOAttack.ATTACK_TYPE_CENTRAL))
        if self.difficulty >= 5:
            bo.append(BOAttack(165, BOAttack.ATTACK_TYPE_OUTLYING))        
        return bo

    def update(self, dt):
        if not self.scene.get_civ_planets(self.civ):
            return
        if self.duration_edge(60):
            if self.attack_to:
                self.attack_to.upgradeable = True
            self.attack_from = random.choice(self.scene.get_civ_planets(self.civ))
            self.attack_to = random.choice(self.scene.get_civ_planets(self.scene.player_civ))

            # Don't do the curse too early or at beginning difficulty
            if self.difficulty > 1 and self.time > 60:
                if not self.curse:
                    self.curse = Alien2CurseIndicator(self.attack_to)
                    self.scene.game_group.add(self.curse)
                else:
                    self.curse.planet = self.attack_to
                    self.curse.pos  = V2(self.attack_to.pos)
                    self.curse._generate_image()
                self.attack_to.upgradeable = False
                
        return super().update(dt)

    def get_attacking_ships(self):
        return ['alien2fighter', 'alien2controlship', 'fighter', 'bomber', 'interceptor', 'battleship']

    def get_colonist(self):
        return 'alien2colonist'

alien.ALIENS['alien2'] = Alien2
