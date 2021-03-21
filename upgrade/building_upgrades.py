from upgrade.upgrades import register_upgrade, Upgrade
from planet.building import make_simple_stats_building
from stats import Stats

class AddBuildingUpgrade(Upgrade):
    building = None
    def apply(self, to):
        b = to.add_building(self.building)
        b.upgrade = self.name

@register_upgrade
class EconUpgrade(AddBuildingUpgrade):
    name = "econ1"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+25%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'econ', 'parents':[]}
    building = make_simple_stats_building("econ1", stats=Stats(top_mining_rate=0.25), shape="refinery")

@register_upgrade
class Econ2AUpgrade(AddBuildingUpgrade):
    name = "econ2a"
    resource_type = "iron"
    category = "buildings"
    title = "Nuclear Reactor"
    description = "[^+50%] [Mining Rate] for [Primary Resource], [!-2] [Max Population]"
    icon = "nuclearreactor"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ2a", stats=Stats(top_mining_rate=0.5, pop_max_add=-2), shape="nuclearreactor")
    requires = ("econ1",)
    family = {'tree':'econ', 'parents':['econ1']}

@register_upgrade
class Econ2BUpgrade(AddBuildingUpgrade):
    name = "econ2b"
    resource_type = "iron"
    category = "buildings"
    title = "Military Surplus"
    description = "[^+25%] [Mining Rate] for [Primary Resource], [!-50%] [Fighter Production]"
    icon = "militarysurplus"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ2b", stats=Stats(top_mining_rate=0.25, fighter_production_halving=1), shape="militarysurplus")
    requires = ("econ1",)    
    family = {'tree':'econ', 'parents':['econ1']}

@register_upgrade
class Econ3Upgrade(AddBuildingUpgrade):
    name = "econ3"
    resource_type = "iron"
    category = "buildings"
    title = "IO Matrix"
    description = "[^+10%] [Mining Rate] for [Primary Resource] per Building"
    icon = "iomatrix"
    cursor = "allied_planet"
    building = make_simple_stats_building("econ3", stats=Stats(top_mining_per_building=0.1), shape="iomatrix")
    requires = lambda x:"econ1" in x and ("econ2a" in x or "econ2b" in x)
    infinite = True
    family = {'tree':'econ', 'parents':['econ2a','econ2b']}

@register_upgrade
class Health1Upgrade(AddBuildingUpgrade):
    name = "health1"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Planet has [^+50%] [Health]"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health1", stats=Stats(planet_health_mul=0.5), shape="loworbitdefenses")
    family = {'tree':'planethealth', 'parents':[]}

@register_upgrade
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

@register_upgrade
class Health2BUpgrade(AddBuildingUpgrade):
    name = "health2b"
    resource_type = "iron"
    category = "buildings"
    title = "High Orbit Defenses"
    description = "Grants [^+10] [Health] to Nearby Ships"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health2b", stats=Stats(planet_health_aura=10), shape="highorbitdefenses")
    requires = ("health1",)  
    family = {'tree':'planethealth', 'parents':['health1']}

@register_upgrade
class Health3Upgrade(AddBuildingUpgrade):
    name = "health3"
    resource_type = "iron"
    category = "buildings"
    title = "Auto Artillery"
    description = "When Hit, Planet Fires Back"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building("health3", stats=Stats(planet_thorns=1), shape="autoartillery")
    requires = lambda x:'health1' in x and ('health2a' in x or 'health2b' in x)
    family = {'tree':'planethealth', 'parents':['health2a','health2b']}

@register_upgrade
class Pop1Upgrade(AddBuildingUpgrade):
    name = "pop1"
    resource_type = "iron"
    category = "buildings"
    title = "Modular Dwellings"
    description = "[^+33%] Maximum Population"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':[]}
    building = make_simple_stats_building("pop1", stats=Stats(pop_max_mul=0.33), shape="modulardwellings")

@register_upgrade
class Pop2aUpgrade(AddBuildingUpgrade):
    name = "pop2a"
    resource_type = "iron"
    category = "buildings"
    title = "Life Support"
    description = "[^+2] Maximum Population"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['pop1']}
    building = make_simple_stats_building("pop1", stats=Stats(pop_max_add=2), shape="lifesupport")
    requires = ('pop1',)

@register_upgrade
class Pop2bUpgrade(AddBuildingUpgrade):
    name = "pop2b"
    resource_type = "iron"
    category = "buildings"
    title = "Armory"
    description = "For each [Population], planet fires [1] missile at nearby enemy ships"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['pop1']}
    building = "pop2b"
    requires = ('pop1',)

@register_upgrade
class Pop3Upgrade(AddBuildingUpgrade):
    name = "pop3"
    resource_type = "iron"
    category = "buildings"
    title = "Underground Shelter"
    description = "[^+25%] [Max Population], [!-30%] [Max Health]"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['pop2a', 'pop2b']}
    building = make_simple_stats_building("pop3", stats=Stats(pop_max_mul=0.25, planet_health_mul=-0.30), shape="undergroundshelter")
    requires = lambda x:'pop1' in x and ('pop2a' in x or 'pop2b' in x)
    infinite = True

@register_upgrade
class Hangar1Upgrade(AddBuildingUpgrade):
    name = "hangar1"
    resource_type = "iron"
    category = "buildings"
    title = "Fighter Hangar"
    description = "[^+33%] [Fighter] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':[]}
    building = make_simple_stats_building("hangar1", stats=Stats(fighter_production=0.33), shape="modulardwellings")

@register_upgrade
class Hangar2aUpgrade(AddBuildingUpgrade):
    name = "hangar2a"
    resource_type = "ice"
    category = "buildings"
    title = "Interceptor Hangar"
    description = "Unlock Interceptors. [^+50%] [Interceptor] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['hangar1']}
    building = make_simple_stats_building("hangar2a", stats=Stats(interceptor_production=0.5), shape="lifesupport")
    requires = ('hangar1',)

@register_upgrade
class Hangar2bUpgrade(AddBuildingUpgrade):
    name = "hangar2b"
    resource_type = "ice"
    category = "buildings"
    title = "Bomber Hangar"
    description = "Unlock Bombers. [^+50%] [Bomber] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['hangar1']}
    building = make_simple_stats_building("hangar2b", stats=Stats(bomber_production=0.5), shape="lifesupport")
    requires = ('hangar1',)

@register_upgrade
class Hangar3Upgrade(AddBuildingUpgrade):
    name = "hangar3"
    resource_type = "gas"
    category = "buildings"
    title = "Battleship Hangar"
    description = "Unlock Battleships. [^+10%] [Battleship] Production Speed"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['hangar2a', 'hangar2b']}
    building = make_simple_stats_building("hangar3", stats=Stats(battleship_production=0.5), shape="lifesupport")
    requires = lambda x:'hangar1' in x and ('hangar2a' in x or 'hangar2b' in x)
    infinite = True     
    
@register_upgrade
class GrowthUpgrade(AddBuildingUpgrade):
    name = "growth1"
    resource_type = "ice"
    category = "buildings"
    title = "Farm"
    description = "[^+33%] faster Population growth rate"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'growth', 'parents':[]}
    building = make_simple_stats_building("growth", stats=Stats(pop_growth_rate=0.33), shape="refinery")
    infinite=True

@register_upgrade
class ScarcestResourceUpgrade(AddBuildingUpgrade):
    name = "scarcest1"
    resource_type = "gas"
    category = "buildings"
    title = "Strip Mining"
    description = "[^+25%] faster mining rate for the scarcest available resource"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':[]}
    building = make_simple_stats_building("scarcest", stats=Stats(scarcest_mining_rate=0.25), shape="refinery")
    infinite=True