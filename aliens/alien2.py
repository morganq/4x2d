from resources import resource_path
from spritebase import SpriteBase
from aliens import alien
from helper import clamp
from upgrade.building_upgrades import AddBuildingUpgrade, make_simple_stats_building
from productionorder import ProductionOrder
from stats import Stats
from planet import building as buildings
from upgrade.upgrades import register_upgrade, Upgrade
from aliens.alien2battleship import Alien2Battleship
import random
from v2 import V2
import pygame
from colors import *

from aliens import alien2battleship
from aliens import alien2colonist
from aliens import alien2fighter
from aliens import alien2controlship

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

    def apply(self, to):
        p = ProductionOrder("alien2controlship", 1, 10)
        to.add_production(p)

@register_upgrade
class Alien2FighterProductionUpgrade3(Alien2FighterProductionUpgrade1):
    name = "alien2battleship"
    resource_type = "gas"    

    def apply(self, to):
        found_ship = None
        for ship in to.scene.get_civ_ships(to.owning_civ):
            if isinstance(ship, Alien2Battleship):
                found_ship = ship
                break

        if found_ship and not found_ship.constructed:
            found_ship.frame += 1
            if found_ship.frame == 2:
                found_ship.constructed = True
                target = random.choice(to.scene.get_civ_planets(to.scene.my_civ))
                found_ship.set_target(target)
        else:
            pos = to.pos + V2.random_angle() * (to.radius + 20)
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
    stats = Stats(alien_control_mul=-0.25)
    

@register_upgrade
class Alien2Tech1Upgrade3(Alien2Tech1Upgrade):
    name = "alien2techrof3"
    resource_type = "gas"

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
    building = make_simple_stats_building(stats=Stats(mining_rate=0.33), shape="modulardwellings")
    infinite = True

@register_upgrade
class Alien2EconUpgrade2(Alien2EconUpgrade):
    name = "alien2econpop2"
    resource_type = "ice"
    building = make_simple_stats_building(stats=Stats(mining_gas_per_iron=0.5), shape="modulardwellings")

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
            p1 = V2.from_angle(theta) * (self.planet.radius + d)
            p2 = V2.from_angle(theta + 0.05) * (self.planet.radius + d + 5)
            p3 = V2.from_angle(theta) * (self.planet.radius + d + 4)
            p4 = V2.from_angle(theta - 0.05) * (self.planet.radius + d + 5)
            pts = [(p + c).tuple() for p in [p1,p2,p3,p4]]
            pygame.draw.polygon(self.image, PICO_RED, pts, 0)

        self.image.blit(cancel, (c - V2(4,4)).tuple())

        self._recalc_rect()


class Alien2(alien.Alien):
    name = "alien2"
    title = "ALIEN CIV 2"
    ATTACK_DURATION = 15
    DEFEND_DURATION = 3
    EXPAND_NUM_NEAREST = 1
    EXPAND_DURATION = 60
    tips = [
        ("assets/alien2fighter.png", "ALIEN CIV 2 can INTIMIDATE a planet, preventing new buildings or ships from being made there."),
        ("assets/alien2controlship.png", "Infiltrators can DOMINATE and take control of your ships unless you destroy them quickly."),
        ("assets/alien2battleship.png", "[Motherships] take a long time to build, but can defeat a whole fleet in combat.")
    ]    

    def __init__(self, scene, civ):
        super().__init__(scene, civ)
        self.attack_from = None
        self.attack_to = None
        self.pick_new_target_time = 0
        self.curse = None

    def update(self, dt):
        self.pick_new_target_time += dt
        if self.duration_edge(60):
            if self.attack_to:
                self.attack_to.upgradeable = True
            self.attack_from = random.choice(self.scene.get_civ_planets(self.civ))
            self.attack_to = random.choice(self.scene.get_civ_planets(self.scene.my_civ))

            # Don't do the curse too early or at beginning difficulty
            if self.difficulty > 1 and self.time > 60:
                if not self.curse:
                    self.curse = Alien2CurseIndicator(self.attack_to)
                    self.scene.game_group.add(self.curse)
                else:
                    self.curse.planet = self.attack_to
                    self.curse.pos = self.attack_to.pos.copy()
                    self.curse._generate_image()
                self.attack_to.upgradeable = False
                
        return super().update(dt)

    def set_difficulty(self, difficulty):
        super().set_difficulty(difficulty)
        self.EXPAND_DURATION = max(30 - (difficulty * 2), 10)

    def get_resource_priority_odds(self):
        if self.time < 180 and self.fear_attack:
            return {'produce':0.95, 'grow':0.05,'tech':0}
        if self.time < 180:
            return {
                'grow':0.3,
                'produce':0.4,
                'tech':0.3
            }
        elif self.time < 300:
            return {
                'grow':0,
                'produce':1,
                'tech':0
            }            
        else:
            return {
                'grow':0.2,
                'produce':0.5,
                'tech':0.3
            }

    def get_attack_chance(self, my_planet, target):
        if target == self.attack_to:
            for ship in self.scene.get_civ_ships(self.civ):
                if ship.chosen_target == target:
                    return 1
            if self.time > self.last_attack_time + (120 - self.difficulty * 8):
                return 1
            return 0.15
        if target.health <= 0:
            return 1
        return 0

    def _get_possible_attack_targets(self, planet):
        if self.attack_to:
            return [self.attack_to]
        return []

    def get_expand_chance(self, planet):    
        if len(self.scene.get_civ_planets(self.civ)) < 3:
            return 0.1 * planet.population
        else:
            return 0.01 * planet.population

    def get_defend_chance(self, my_planet, target):
        if self.attack_from == target and sum(my_planet.ships.values()) > 0:
            if (my_planet.pos - self.attack_to.pos).sqr_magnitude() < (self.attack_from.pos - self.attack_to.pos).sqr_magnitude():
                return 0
            else:
                return 1
        return 0

    def get_attacking_ships(self):
        return ['alien2fighter', 'alien2controlship', 'fighter', 'bomber', 'interceptor', 'battleship']

    def get_colonist(self):
        return 'alien2colonist'

alien.ALIENS['alien2'] = Alien2