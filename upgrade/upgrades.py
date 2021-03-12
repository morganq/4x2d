from productionorder import ProductionOrder
from colors import *
from stats import Stats
from collections import defaultdict
from planet.building import make_simple_stats_building

UPGRADES = {
    'iron':defaultdict(list),
    'ice':defaultdict(list),
    'gas':defaultdict(list)
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
    stats = Stats()
    requires = ()
    infinite = False
    family = None
    def apply(self, to):
        pass


UPGRADE_CLASSES = {}
ALL_UPGRADE_CLASSES = []

def upgrade(cls):
    UPGRADE_CLASSES[cls.name] = cls
    UPGRADES[cls.resource_type][cls.category].append(cls.name)
    ALL_UPGRADE_CLASSES.append(cls)
    return cls


class AddBuildingUpgrade(Upgrade):
    building = None
    def apply(self, to):
        to.add_building(self.building)

@upgrade
class EconUpgrade(AddBuildingUpgrade):
    name = "econ1"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+15%] [Mining Rate] for [Primary Resource]"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'econ', 'parents':[]}
    building = make_simple_stats_building("econ1", stats=Stats(top_mining_rate=0.15), shape="test")

@upgrade
class Econ2AUpgrade(AddBuildingUpgrade):
    name = "econ2a"
    resource_type = "iron"
    category = "buildings"
    title = "Nuclear Reactor"
    description = "[^+35%] [Mining Rate] for [Primary Resource], [!-2] [Population]"
    icon = "mining"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ2a", stats=Stats(top_mining_rate=0.35, pop_max_add=-2), shape="test")
    requires = ("econ1",)
    family = {'tree':'econ', 'parents':['econ1']}

@upgrade
class Econ2BUpgrade(AddBuildingUpgrade):
    name = "econ2b"
    resource_type = "iron"
    category = "buildings"
    title = "Military Surplus"
    description = "[^+25%] [Mining Rate] for [Primary Resource], [!-50%] [Fighter Production]"
    icon = "mining"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ2b", stats=Stats(top_mining_rate=0.25, fighter_production_halving=1), shape="test")
    requires = ("econ1",)    
    family = {'tree':'econ', 'parents':['econ1']}

@upgrade
class Econ3Upgrade(AddBuildingUpgrade):
    name = "econ3"
    resource_type = "iron"
    category = "buildings"
    title = "IO Matrix"
    description = "[^+5%] [Mining Rate] for [Primary Resource] per Building"
    icon = "mining"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ3", stats=Stats(top_mining_per_building=0.05), shape="test")
    requires = lambda x:"econ1" in x and ("econ2a" in x or "econ2b" in x)
    infinite = True
    family = {'tree':'econ', 'parents':['econ2a','econ2b']}

@upgrade
class Health1Upgrade(AddBuildingUpgrade):
    name = "health1"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Planet has [^+50%] [Health]"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health1", stats=Stats(planet_health_mul=0.5), shape="test")
    family = {'tree':'planethealth', 'parents':[]}

@upgrade
class Health2AUpgrade(AddBuildingUpgrade):
    name = "health2a"
    resource_type = "iron"
    category = "buildings"
    title = "Repair Bay"
    description = "Planet Regenerates [^+1] [Health/Sec]"
    icon="planetregen"
    cursor = "allied_planet"
    building = "regen"
    requires = ("health1",)
    family = {'tree':'planethealth', 'parents':['health1']}

@upgrade
class Health2BUpgrade(AddBuildingUpgrade):
    name = "health2b"
    resource_type = "iron"
    category = "buildings"
    title = "High Orbit Defenses"
    description = "Grants [^+10] [Health] to Nearby Ships"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health2b", stats=Stats(planet_health_aura=10), shape="test")
    requires = ("health1",)  
    family = {'tree':'planethealth', 'parents':['health1']}

@upgrade
class Health3Upgrade(AddBuildingUpgrade):
    name = "health3"
    resource_type = "iron"
    category = "buildings"
    title = "Auto Artillery"
    description = "When Hit, Planet Fires Back"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health3", stats=Stats(planet_thorns=1), shape="test")
    requires = lambda x:'health1' in x and ('health2a' in x or 'health2b' in x)
    family = {'tree':'planethealth', 'parents':['health2a','health2b']}

@upgrade
class ArmoryUpgrade(AddBuildingUpgrade):
    name = "armory"
    resource_type = "gas"
    category = "buildings"
    title = "Armory"
    description = "Workers Attack Nearby Ships"
    icon = "militia"
    cursor = "allied_planet"
    building = "armory"

@upgrade
class FightersUpgrade(Upgrade):
    name = "fighters"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "[^6] [Fighters] Over [40 seconds]"
    icon = "fighters6"
    cursor = "allied_planet"
    infinte = True

    def apply(self, to):
        p = ProductionOrder("fighter", 6, 40)
        to.add_production(p)

@upgrade
class FightersLongUpgrade(Upgrade):
    name = "fighterslong"
    resource_type = "ice"
    category = "ships"
    title = "Extended Contract"
    description = "[^30] [Fighters] Over [3 minutes]"
    icon = "fighters30"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 30, 180)
        to.add_production(p)

@upgrade
class FightersNowUpgrade(Upgrade):
    name = "fightersnow"
    resource_type = "gas"
    category = "ships"
    title = "Emergency Supplies"
    description = "[^3] [Fighters] and [^+3] [population] instantly"
    icon = "fighters3pop"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)
        to.population += 3

@upgrade
class RateOfFireUpgrade(Upgrade):
    name = "rate_of_fire"
    resource_type = "iron"
    category = "tech"
    title = "Rapid Fire"
    description = "[^+15%] [Rate of Fire]"
    icon = "rateoffire"
    stats = Stats(fire_rate = 0.15)

@upgrade
class ArmorUpgrade(Upgrade):
    name = "armor"
    resource_type = "ice"
    category = "tech"
    title = "Fragment Plating"
    description = "[^+25%] [Health] for [All Ships]"
    icon="armor"
    stats = Stats(ship_health = 0.15)

@upgrade
class WarpUpgrade(Upgrade):
    name = "warp"
    resource_type = "gas"
    category = "tech"
    title = "Warp Drive"
    description = "[^+15] [Warp Drive Distance]"
    icon = "warp"
    stats = Stats(warp_drive=50)
