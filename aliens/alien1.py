from colors import PICO_BROWN, PICO_SKIN
from helper import clamp
from planet import building as buildings
from productionorder import ProductionOrder
from stats import Stats
from upgrade.building_upgrades import (AddBuildingUpgrade,
                                       make_simple_stats_building)
from upgrade.upgrades import Upgrade, register_upgrade

from aliens import (alien, alien1battleship, alien1colonist, alien1fighter,
                    alien1warpship)
from aliens.buildorder import *


@register_upgrade
class Alien1FighterProductionUpgrade(Upgrade):
    name = "alien1fighters"
    resource_type = "iron"
    category = "ships"
    title = "Alien Fighter Production"
    description = "[^3] [Fighters] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien1'
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien1fighter", 3, 10)
        to.add_production(p)

@register_upgrade
class Alien1FighterProductionUpgradeIce(Alien1FighterProductionUpgrade):
    name = "alien1warpship"
    resource_type = "ice"
    category = "ships"
    title = "Alien Warpship Production"
    description = "[^2] [Warpship] Over 90 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien1'
    infinite = True
    alien_min_level = 4

    def apply(self, to):
        p = ProductionOrder("alien1warpship", 2, 90)
        to.add_production(p)

@register_upgrade
class Alien1FighterProductionUpgrade(Upgrade):
    name = "alien1battleship"
    resource_type = "gas"
    category = "ships"
    title = "Alien Battleship Production"
    description = "[^1] [Battleship] Over 60 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien1'
    infinite = True
    alien_min_level = 7

    def apply(self, to):
        if to.owning_civ.alien.difficulty > 1:
            p = ProductionOrder("alien1battleship", 1, 60)
            to.add_production(p)

@register_upgrade
class Alien1Tech1Upgrade(Upgrade):
    name = "alien1techrof"
    resource_type = "iron"
    category = "tech"
    title = "Alien Tech"
    description = "[Alien Fighters] gain [^+15%] rate of fire"
    icon = "preciseassembly"
    stats = Stats(ship_fire_rate=0.15)
    requires = None
    alien = True
    alien_name = 'alien1'
    infinite = True

@register_upgrade
class Alien1Tech2Upgrade(Upgrade):
    name = "alien1techwarp"
    resource_type = "ice"
    category = "tech"
    title = "Alien Tech 2"
    description = "[Alien Fighters] gain [^+2] warp drive"
    icon = "preciseassembly"
    stats = Stats(warp_drive=2)
    requires = None
    alien = True
    alien_name = 'alien1'
    infinite = True

    alien_min_level = 4

@register_upgrade
class Alien1TechUpgradeGas(Alien1Tech1Upgrade):
    resource_type = "gas"    

@register_upgrade
class Alien1EconUpgrade(AddBuildingUpgrade):
    name = "alien1econrate"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+15%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'alien1'
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.15), shape="barysidrill")
    infinite = True

@register_upgrade
class Alien1EconUpgradeIce(AddBuildingUpgrade):
    name = "alien1econpop"
    resource_type = "ice"
    category = "buildings"
    title = "Refinery"
    description = "[^+2] max pop"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'alien1'
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="barysipop")
    infinite = True

@register_upgrade
class Alien1EconUpgradeGas(Alien1EconUpgradeIce):   
    resource_type = "gas"         
    alien_name = 'alien1'

class Alien1(alien.Alien):
    name = "alien1"
    EXPAND_NUM_NEAREST = 3
    title = "BARYSI NOMADS"
    COLOR = PICO_BROWN

    quotes = [
        "\"Every vein and shard in this system belongs to us.\""
    ]

    tips = [
        ("assets/alieninfo-terraform.png", "The BARYSI Terraform all planets they colonize, in order to extract more valuable ice and gas"),
        ("assets/alieninfo-warpship.png", "BARYSI'S Defensive AEGIS ships are tethered to their host planet and are equipped with an explosive payload"),
        ("assets/alieninfo-crusher.png", "CRUSHERS are heavy Barysi battleships that can warp across the galaxy")
    ]

    def get_build_order_steps(self):
        bo = [
            BOExpand(3),
            BOExpand(4),
            BOExpand(5),
            BOResearch(10, "alien1econrate"),
            BOResearch(30, "alien1fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(40, "alien1econpop", "alien1econrate"),
            BOResearch(50, "alien1techwarp", "alien1econrate"),
            BOAttack(55, attack_type=BOAttack.ATTACK_TYPE_RANDOM, attack_strength=0.1),
            BOExpand(65),
            BOResearch(65, "alien1warpship", "alien1fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(75, "alien1warpship", "alien1fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),            
            BOResearch(70, "alien1techrof"),
            BOResearch(80, "alien1econpop", "alien1econrate"),
            BOResearch(90, "alien1warpship", "alien1fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOResearch(90, "alien1fighters", target_type=BOResearch.TARGET_TYPE_UNDEFENDED),
            BOAttack(95, attack_type=BOAttack.ATTACK_TYPE_RANDOM, attack_strength=0.1),
            BOResearch(110, "alien1battleship", "alien1warpship"),
            BOResearch(120, "alien1techwarp", "alien1techrof"),
            BOResearch(140, "alien1techwarp", "alien1techrof"),
            BOResearch(150, "alien1battleship", "alien1warpship"),
        ]

        if self.difficulty >= 3:
            bo.append(BOAttack(145, BOAttack.ATTACK_TYPE_RANDOM))
        if self.difficulty >= 5:
            bo.append(BOAttack(155, BOAttack.ATTACK_TYPE_RANDOM))        
        return bo        

    def set_difficulty(self, difficulty):
        super().set_difficulty(difficulty)

        my_planet = self.scene.get_civ_planets(self.civ)[0]
        if self.difficulty >= 3:
            my_planet.add_ship("alien1warpship")
            my_planet.add_ship("alien1warpship")

        self.starting_num_planets = len(self.scene.get_civ_planets(self.civ))


    def get_colonist(self):
        return "alien1colonist"

    def get_attacking_ships(self):
        return ['alien1fighter', 'alien1battleship']

alien.ALIENS['alien1'] = Alien1
