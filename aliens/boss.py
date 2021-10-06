from colors import *
from helper import clamp
from planet import building as buildings
from productionorder import ProductionOrder
from stats import Stats
from upgrade.building_upgrades import (AddBuildingUpgrade,
                                       make_simple_stats_building)
from upgrade.upgrades import Upgrade, register_upgrade

from aliens import alien, bosscolonist, bossfighter, bosslaser
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
    name = "bosswarpship"
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
        super().set_difficulty(difficulty)
        #self.EXPAND_DURATION = max(40 - (difficulty * 2), 10)
        self.EXPAND_DURATION = 10

        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.add_building(BossHomeDefenseUpgrade)

        self.starting_num_planets = len(self.scene.get_civ_planets(self.civ))

    def get_resource_priority_odds(self):
        if self.time < 180 and self.fear_attack:
            return {'produce':0.85, 'grow':0.05,'tech':0.1}
        if self.time < 180:
            return {
                'grow':0.5,
                'produce':0.2,
                'tech':0.3
            }        
        else:
            return {
                'grow':0.2,
                'produce':0.45,
                'tech':0.35
            }             

    def get_attack_chance(self, my_planet, target):
        odds = 0
        if not self.build_order.is_over():
            bostep = self.build_order.get_current_step(self.time)
            if bostep and bostep.name == "attack":
                print("Attacking because it's the build order")
                odds = 1
            else:
                odds = 0

        elif self.time > self.last_attack_time + (120 - self.difficulty * 8):
            print("Attacking because it's been %d seconds" % (120 - self.difficulty * 8))
            odds = 1

        elif my_planet.ships['bossbattleship'] > 0:
            print("Attacking because we have a battleship")
            return 1

        else:
            print("Random chance to attack")
            odds = 0.1

        if self.count_attacking_ships() < self.get_max_attackers():
            return odds
        else:
            print("May have attacked, but at max attackers", self.get_max_attackers())
            return 0

    def get_colonist(self):
        return "bosscolonist"

    def _get_possible_expand_targets(self, planet):
        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())

        num_planets = len(self.scene.get_civ_planets(self.civ))
        if num_planets > self.starting_num_planets:
            near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:3]
        else:
            near_unclaimed = [p for p in near_planets if p.owning_civ == None][-4:]

        return near_unclaimed

    def get_expand_chance(self, planet):    
        if not self.build_order.is_over():
            bostep = self.build_order.get_current_step(self.time)
            if bostep and bostep.name == "expand":
                self.build_order.completed_current_step()
                return 1
            else:
                return 0

        num_planets = len(self.scene.get_civ_planets(self.civ))
        z = clamp((120 - self.time) / 20, 1, 3)
        if num_planets < 4:
            odds = 0.15 * (planet.population-1) * z
        else:
            odds = 0.009 * planet.population

        colonists_out = self.count_expanding_ships()

        return odds / (colonists_out + 1)

    def get_defend_chance(self, my_planet, target):
        return 0

    def get_max_attackers(self):
        curve = {
            1: 0,
            2: 3,
            3: 4,
            4: 4,
            5: 5,
            6: 7,
        }.get(self.difficulty, 999)        

        if self.difficulty > 1 and self.time > 300:
            curve *= 2

        return curve

    def get_attacking_ships(self):
        return ['bossfighter', 'bosslaser']

alien.ALIENS['boss'] = Boss