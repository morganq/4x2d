from colors import *
from helper import clamp
from planet import building as buildings
from productionorder import ProductionOrder
from stats import Stats
from upgrade.building_upgrades import (AddBuildingUpgrade,
                                       make_simple_stats_building)
from upgrade.upgrades import Upgrade, register_upgrade

from aliens import alien, bosscolonist, bossfighter, bosslaser, buildorder
from aliens.buildorder import *


@register_upgrade
class BossHomeDefenseUpgrade(AddBuildingUpgrade):
    name = "bosshomedefense"
    resource_type = "iron"
    category = "buildings"
    title = "Alien Home Defense"
    description = "Planet fires missiles at nearby enemy ships"
    icon = "mining"
    family = {}
    building = buildings.AlienHomeDefenseBuilding
    requires = lambda x: False
    alien = True
    alien_name = 'boss'

@register_upgrade
class BossFighterProductionUpgrade(Upgrade):
    name = "bossfighters"
    resource_type = "iron"
    category = "ships"
    title = "Alien Fighter Production"
    description = "[^2] [Fighters] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'boss'
    infinite = True

    def apply(self, to):
        p = ProductionOrder("bossfighter", 2, 10)
        to.add_production(p)

@register_upgrade
class BossFighterProductionUpgradeIce(BossFighterProductionUpgrade):
    name = "bosslaser"
    resource_type = "ice"
    category = "ships"
    title = "Alien Warpship Production"
    description = "[^2] [Lasership] Over 60 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'boss'
    infinite = True
    alien_min_level = 4

    def apply(self, to):
        p = ProductionOrder("bosslaser", 2, 60)
        to.add_production(p)

@register_upgrade
class BossFighterProductionUpgrade(Upgrade):
    name = "bossbattleship"
    resource_type = "gas"
    category = "ships"
    title = "Alien Battleship Production"
    description = "[^1] [Battleship] Over 60 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'boss'
    infinite = True
    alien_min_level = 7

    def apply(self, to):
        if to.owning_civ.alien.difficulty > 1:
            p = ProductionOrder("bosslaser", 1, 60)
            to.add_production(p)

@register_upgrade
class BossTech1Upgrade(Upgrade):
    name = "bosstechrof"
    resource_type = "iron"
    category = "tech"
    title = "Alien Tech"
    description = "[Alien Fighters] gain [^+15%] rate of fire"
    icon = "preciseassembly"
    stats = Stats(ship_fire_rate=0.15)
    requires = None
    alien = True
    alien_name = 'boss'
    infinite = True

@register_upgrade
class BossTech2Upgrade(Upgrade):
    name = "bosstechwarp"
    resource_type = "ice"
    category = "tech"
    title = "Alien Tech 2"
    description = "[Alien Fighters] gain [^+2] warp drive"
    icon = "preciseassembly"
    stats = Stats(warp_drive=2)
    requires = None
    alien = True
    alien_name = 'boss'
    infinite = True

    alien_min_level = 4

@register_upgrade
class BossTechUpgradeGas(BossTech1Upgrade):
    resource_type = "gas"    

@register_upgrade
class BossEconUpgrade(AddBuildingUpgrade):
    name = "bosseconrate"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+15%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'boss'
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.15), shape="refinery")
    infinite = True

@register_upgrade
class BossEconUpgradeIce(AddBuildingUpgrade):
    name = "bosseconpop"
    resource_type = "ice"
    category = "buildings"
    title = "Refinery"
    description = "[^+2] max pop"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'boss'
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="modulardwellings")
    infinite = True

@register_upgrade
class BossEconUpgradeGas(BossEconUpgradeIce):   
    resource_type = "gas"         
    alien_name = 'boss'

class Boss(alien.Alien):
    name = "boss"
    EXPAND_NUM_NEAREST = 3
    title = "CENSORS"
    COLOR = PICO_RED

    quotes = [
        "..."
    ]

    tips = [
        ("assets/alieninfo-terraform.png", ""),
        ("assets/alieninfo-warpship.png", ""),
        ("assets/alieninfo-crusher.png", "")
    ]

    def get_build_order_steps(self):
        return [
            BOExpand(0),
            BOResearch(0,"bossfighters"),
            BOExpand(20),
            BOResearch(60,"bossfighters"),
            BOAttack(80),
            BOExpand(80),
            BOResearch(130, "bosslaser")
        ]

    def set_difficulty(self, difficulty):
        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.add_building(BossHomeDefenseUpgrade)
        my_planet.population = 10

        self.civ.base_stats['planet_health_mul'] = 2
        self.civ.base_stats['mining_rate'] = 1.5
        self.civ.base_stats['max_ships_per_planet'] = 999

        self.starting_num_planets = len(self.scene.get_civ_planets(self.civ))

        for planet in self.scene.get_civ_planets(self.civ):
            planet.set_health(planet.get_max_health(), False)

        self.build_order = buildorder.BuildOrder(self.get_build_order_steps())        


    def get_colonist(self):
        return "bosscolonist"

    def get_attacking_ships(self):
        return ['bossfighter', 'bosslaser']

alien.ALIENS['boss'] = Boss
