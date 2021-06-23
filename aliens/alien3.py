from aliens import alien
from helper import clamp
from upgrade.building_upgrades import AddBuildingUpgrade, make_simple_stats_building
from productionorder import ProductionOrder
from stats import Stats
from planet import building as buildings
from upgrade.upgrades import register_upgrade, Upgrade
from aliens.alien3battleship import Alien3Battleship
import random
from aliens.alien3void import Alien3Void
from v2 import V2

@register_upgrade
class Alien3HomeDefenseUpgrade(AddBuildingUpgrade):
    name = "a3bhomedefense"
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
    description = "[^1] [Bomber] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    alien_name = 'alien3'
    infinite = True

    def apply(self, to):
        to.add_production(ProductionOrder("alien3bomber", 1, 10))

@register_upgrade
class Alien3FighterProductionUpgrade3(Alien3FighterProductionUpgrade1):
    name = "a3sbattleship"
    resource_type = "gas"    

    def apply(self, to):
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
    building = make_simple_stats_building(stats=Stats(mining_rate=0.33), shape="modulardwellings")
    infinite = True

@register_upgrade
class Alien3EconUpgrade2(Alien3EconUpgrade):
    name = "a3bice"
    resource_type = "ice"
    building = make_simple_stats_building(stats=Stats(), shape="modulardwellings")

@register_upgrade
class Alien3EconUpgrade3(Alien3EconUpgrade):
    name = "a3bgas"
    resource_type = "gas"   
    building = make_simple_stats_building(stats=Stats(), shape="modulardwellings") 

class Alien3(alien.Alien):
    name = "alien3"
    title = "ALIEN CIV 3"
    ATTACK_DURATION = 15
    DEFEND_DURATION = 15
    EXPAND_NUM_NEAREST = 2
    EXPAND_DURATION = 60
    tips = [
        ("assets/alien3fighter.png", "ALIEN CIV 3 produces VOID FIELDS around their planets which grant shields and speed to their ships."),
        ("assets/alien3bomber.png", "The STEALTH BOMBER is invisible within VOID FIELDS."),
        ("assets/alien3battleship.png", "The MOTHERSHIP produces its own VOID FIELDS - like a moving planet!")
    ]    

    def __init__(self, scene, civ):
        super().__init__(scene, civ)
        self.planet_void = {}
        self.ship_void = {}

    def set_difficulty(self, difficulty):
        super().set_difficulty(difficulty)
        self.EXPAND_DURATION = max(30 - (difficulty * 2), 10)

    def update(self, dt):
        if self.difficulty > 1:
            # Create void for planets
            for planet in self.scene.get_civ_planets(self.civ):
                if planet not in self.planet_void:
                    void = Alien3Void(self.scene, planet, planet.get_radius() + 10)
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

        return super().update(dt)

    def grow_void(self):
        for void in self.planet_void.values():
            void.grow()

    def get_resource_priority_odds(self):
        if self.time < 180 and self.fear_attack:
            return {'produce':0.95, 'grow':0.05,'tech':0}
        return {
            'produce':0.3,
            'grow':0.3,
            'tech':0.4
        }

    def get_attack_chance(self, my_planet, target):
        if self.time > self.last_attack_time + 120:
            return 1
        else:
            return sum(my_planet.ships.values()) / 15

    def get_expand_chance(self, planet):    
        if len(self.scene.get_civ_planets(self.civ)) < 3:
            return 0.1 * planet.population
        else:
            return 0.01 * planet.population

    def get_defend_chance(self, my_planet, target):
        return 0

    def get_attacking_ships(self):
        return ['alien3fighter', 'alien3bomber']

    def get_colonist(self):
        return 'alien3colonist'

    def get_voids(self):
        return list(self.planet_void.values()) + list(self.ship_void.values())

alien.ALIENS['alien3'] = Alien3