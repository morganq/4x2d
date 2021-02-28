from productionorder import ProductionOrder
from colors import *

UPGRADES = {
    'iron':{},
    'ice':{},
    'gas':{}
}

UPGRADE_CATEGORY_COLORS = {
    'buildings':PICO_LIGHTGRAY,
    'ships':PICO_GREEN,
    'tech':PICO_ORANGE
}

class Upgrade:
    name = ""
    title = "Not Implemented"
    description = ""
    cursor = None
    icon = None
    def apply(self, to):
        pass


UPGRADE_CLASSES = {}

def upgrade(cls):
    UPGRADE_CLASSES[cls.name] = cls
    UPGRADES[cls.resource_type][cls.category] = [cls.name]
    return cls

@upgrade
class EconUpgrade(Upgrade):
    name = "econ"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "+15% Mining Rate for Primary Resource"
    icon = "mining"
    cursor = "allied_planet"

    def apply(self, to):
        to.add_building("mining_rate")

@upgrade
class RegenUpgrade(Upgrade):
    name = "regen"
    resource_type = "ice"
    category = "buildings"
    title = "Repair Bay"
    description = "Planet regenerates +1 health per second"
    icon="planetregen"
    cursor = "allied_planet"

    def apply(self, to):
        to.add_building("regen")

@upgrade
class ArmoryUpgrade(Upgrade):
    name = "armory"
    resource_type = "gas"
    category = "buildings"
    title = "Armory"
    description = "Workers Attack Nearby Ships"
    icon = "militia"
    cursor = "allied_planet"

    def apply(self, to):
        to.add_building("armory")

@upgrade
class FightersUpgrade(Upgrade):
    name = "fighters"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "6 Fighters Over 40 seconds"
    icon = "fighters6"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 6, 40)
        to.production.append(p)

@upgrade
class FightersLongUpgrade(Upgrade):
    name = "fighterslong"
    resource_type = "ice"
    category = "ships"
    title = "Extended Contract"
    description = "30 Fighters Over 3 minutes"
    icon = "fighters30"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 30, 180)
        to.production.append(p)        

@upgrade
class FightersNowUpgrade(Upgrade):
    name = "fightersnow"
    resource_type = "gas"
    category = "ships"
    title = "Emergency Supplies"
    description = "3 Fighters and +3 population instantly"
    icon = "fighters3pop"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.production.append(p)
        to.population += 3

@upgrade
class RateOfFireUpgrade(Upgrade):
    name = "rate_of_fire"
    resource_type = "iron"
    category = "tech"
    title = "Rapid Fire"
    description = "+15% Rate of Fire"
    icon = "rateoffire"

    def apply(self, to):
        to.upgrade_stats['fire_rate'] += 0.15


@upgrade
class ArmorUpgrade(Upgrade):
    name = "armor"
    resource_type = "ice"
    category = "tech"
    title = "Fragment Plating"
    description = "+25% Health for All Ships"
    icon="armor"

    def apply(self, to):
        to.upgrade_stats['ship_health'] += 0.25

@upgrade
class WarpUpgrade(Upgrade):
    name = "warp"
    resource_type = "gas"
    category = "tech"
    title = "Warp Drive"
    description = "+15 Warp Drive Distance"
    icon = "warp"

    def apply(self, to):
        to.upgrade_stats['warp_drive'] += 50
