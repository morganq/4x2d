from aliens import alien
from helper import clamp
from upgrade.building_upgrades import AddBuildingUpgrade, make_simple_stats_building
from productionorder import ProductionOrder
from stats import Stats
from planet import building as buildings
from upgrade.upgrades import register_upgrade, Upgrade
from aliens.alien2battleship import Alien2Battleship
import random
from aliens.alien3void import Alien3Void
from v2 import V2

@register_upgrade
class Alien3HomeDefenseUpgrade(AddBuildingUpgrade):
    name = "alien3homedefense"
    resource_type = "iron"
    category = "buildings"
    title = "Alien Home Defense"
    description = "Planet fires missiles at nearby enemy ships"
    icon = "mining"
    family = {}
    building = buildings.AlienHomeDefenseBuilding
    requires = lambda x: False
    alien = True
    alien_name = 'alien3'

@register_upgrade
class Alien3FighterProductionUpgrade1(Upgrade):
    name = "alien3fighters"
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
    name = "alien3controlship"
    resource_type = "ice"
    category = "ships"
    title = "Alien Control Ship Production"
    description = "[^1] [Control Ship] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien3'
    infinite = True

    def apply(self, to):
        pass

@register_upgrade
class Alien3FighterProductionUpgrade3(Alien3FighterProductionUpgrade1):
    name = "alien3battleship"
    resource_type = "gas"    

    def apply(self, to):
        pass

@register_upgrade
class Alien3Tech1Upgrade(Upgrade):
    name = "alien3techspeed"
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
    name = "alien3techcontrol"
    resource_type = "ice"
    stats = Stats()
    

@register_upgrade
class Alien3Tech1Upgrade3(Alien3Tech1Upgrade):
    name = "alien3techrof3"
    resource_type = "gas"

@register_upgrade
class Alien3EconUpgrade(AddBuildingUpgrade):
    name = "alien3econrate"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+33%] mining rate"
    icon = "refinery"
    requires = None
    alien = True
    alien_name = 'alien3'
    building = make_simple_stats_building(stats=Stats(mining_rate=0.33), shape="modulardwellings")
    infinite = True

@register_upgrade
class Alien3EconUpgrade2(Alien3EconUpgrade):
    name = "alien3econpop2"
    resource_type = "ice"
    building = make_simple_stats_building(stats=Stats(), shape="modulardwellings")

@register_upgrade
class Alien3EconUpgrade3(Alien3EconUpgrade):
    name = "alien3econpop3"
    resource_type = "gas"    

class Alien3(alien.Alien):
    name = "alien3"
    title = "ALIEN CIV 3"
    ATTACK_DURATION = 15
    DEFEND_DURATION = 15
    EXPAND_NUM_NEAREST = 2
    EXPAND_DURATION = 60
    tips = [
        ("assets/alien-fighter.png", ""),
        ("assets/alien2controlship.png", ""),
        ("assets/alien2battleship.png", "")
    ]    

    def __init__(self, scene, civ):
        super().__init__(scene, civ)
        self.planet_void = {}

    def set_difficulty(self, difficulty):
        super().set_difficulty(difficulty)
        self.EXPAND_DURATION = max(30 - (difficulty * 2), 10)

    def update(self, dt):
        for planet in self.scene.get_civ_planets(self.civ):
            if planet not in self.planet_void:
                void = Alien3Void(self.scene, planet.pos, planet.get_radius() + 10)
                self.planet_void[planet] = void
                self.scene.game_group.add(void)

        for planet in list(self.planet_void.keys()):
            if planet.owning_civ != self.civ:
                self.planet_void[planet].kill()
                del self.planet_void[planet]

        return super().update(dt)

    def grow_void(self):
        for void in self.planet_void.values():
            void.grow()

    def get_resource_priority_odds(self):
        if self.time < 180 and self.fear_attack:
            return {'produce':0.95, 'grow':0.05,'tech':0}
        return {
            'produce':0,
            'grow':0,
            'tech':1
        }

    def get_attack_chance(self, my_planet, target):
        return sum(my_planet.ships.values()) / 15

    def get_expand_chance(self, planet):    
        if len(self.scene.get_civ_planets(self.civ)) < 3:
            return 0.1 * planet.population
        else:
            return 0.01 * planet.population

    def get_defend_chance(self, my_planet, target):
        return 0

    def get_attacking_ships(self):
        return ['alien3fighter']

    def get_colonist(self):
        return 'alien3colonist'

alien.ALIENS['alien3'] = Alien3