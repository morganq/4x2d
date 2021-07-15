import defensematrix
import portal
from planet import building
from planet import building as buildings
from planet.building import *
from productionorder import PermanentHangarProductionOrder
from stats import Stats

from upgrade.upgrades import Upgrade, register_upgrade


class AddBuildingUpgrade(Upgrade):
    building = None
    def apply(self, to):
        self.building.upgrade = type(self)
        to.add_building(self)

#####################
# Econ - light gray #
#####################
@register_upgrade
class EconUpgrade(AddBuildingUpgrade):
    name = "b_econ1"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+50%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'econ', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.5), shape="refinery")

@register_upgrade
class Econ2AUpgrade(AddBuildingUpgrade):
    name = "b_econ2a"
    resource_type = "iron"
    category = "buildings"
    title = "Nuclear Reactor"
    description = "[^+100%] [Mining Rate] for [Primary Resource], [!No more Buildings can be constructed here]"
    icon = "nuclearreactor"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=1, prevent_buildings=1), shape="nuclearreactor")
    requires = ("b_econ1",)
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ2BUpgrade(AddBuildingUpgrade):
    name = "b_econ2b"
    resource_type = "iron"
    category = "buildings"
    title = "Military Surplus"
    description = "[^+50%] [Mining Rate] for [Primary Resource], [!-50%] [Fighter Production]"
    icon = "militarysurplus"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.50, fighter_production_amt_halving=1), shape="militarysurplus")
    requires = ("b_econ1",)    
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ3Upgrade(AddBuildingUpgrade):
    name = "b_econ3"
    resource_type = "iron"
    category = "buildings"
    title = "IO Matrix"
    description = "[^+15%] [Mining Rate] for [Primary Resource] per Building"
    icon = "iomatrix"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_per_building=0.15), shape="iomatrix")
    requires = lambda x:"econ1" in x and ("b_econ2a" in x or "b_econ2b" in x)
    infinite = True
    family = {'tree':'econ', 'parents':['b_econ2a','b_econ2b']}

####################
# Pop - skin color #
####################
@register_upgrade
class Pop1Upgrade(AddBuildingUpgrade):
    name = "b_pop1"
    resource_type = "iron"
    category = "buildings"
    title = "Modular Dwellings"
    description = "[^+2] Maximum Population"
    icon = "modulardwellings"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="modulardwellings")

@register_upgrade
class Pop2aUpgrade(AddBuildingUpgrade):
    name = "b_pop2a"
    resource_type = "iron"
    category = "buildings"
    title = "Life Support"
    description = "[^+40%] Maximum Population"
    icon = "lifesupport"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = make_simple_stats_building(stats=Stats(pop_max_mul=0.4), shape="lifesupport")
    requires = ('b_pop1',)

@register_upgrade
class Pop2bUpgrade(AddBuildingUpgrade):
    name = "b_pop2b"
    resource_type = "iron"
    category = "buildings"
    title = "University"
    description = "Ship production is [^+15%] faster for each population"
    icon = "university"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = make_simple_stats_building(stats=Stats(ship_production_per_pop=0.15), shape="lifesupport")
    requires = ('b_pop1',)

@register_upgrade
class Pop3Upgrade(AddBuildingUpgrade):
    name = "b_pop3"
    resource_type = "iron"
    category = "buildings"
    title = "Underground Shelter"
    description = "[^+100%] population growth rate"
    icon = "undergroundshelter"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop2a', 'b_pop2b']}
    building = make_simple_stats_building(stats=Stats(pop_growth_rate=1), shape="undergroundshelter")
    requires = lambda x:'b_pop1' in x and ('b_pop2a' in x or 'b_pop2b' in x)
    infinite = True

#################
# Hangar - Pink #
#################
@register_upgrade
class Hangar1Upgrade(AddBuildingUpgrade):
    name = "b_hangar1"
    resource_type = "iron"
    category = "buildings"
    title = "Fighter Hangar"
    description = "[^+50%] [Fighter] Production Quantity"
    icon = "fighterhangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(fighter_production_amt=0.5), shape="modulardwellings")

@register_upgrade
class Hangar2aUpgrade(AddBuildingUpgrade):
    name = "b_hangar2a"
    resource_type = "iron"
    category = "buildings"
    title = "Interceptor Hangar"
    description = "[^+100%] [Interceptor] Production Quantity"
    icon = "interceptorhangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar1']}
    building = make_simple_stats_building(stats=Stats(interceptor_production=1), shape="lifesupport")
    requires = ('b_hangar1',)

@register_upgrade
class Hangar2bUpgrade(AddBuildingUpgrade):
    name = "b_hangar2b"
    resource_type = "iron"
    category = "buildings"
    title = "Bomber Hangar"
    description = "[^+100%] [Bomber] Production Quantity"
    icon = "bomberhangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar1']}
    building = make_simple_stats_building(stats=Stats(bomber_production=1), shape="lifesupport")
    requires = ('b_hangar1',)

@register_upgrade
class Hangar3Upgrade(AddBuildingUpgrade):
    name = "b_hangar3"
    resource_type = "iron"
    category = "buildings"
    title = "Battleship Hangar"
    description = "[^+150%] [Battleship] Production Speed"
    icon = "battleshiphangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar2a', 'b_hangar2b']}
    building = make_simple_stats_building(stats=Stats(battleship_production=1.5), shape="lifesupport")
    requires = lambda x:'b_hangar1' in x and ('b_hangar2a' in x or 'b_hangar2b' in x)
    infinite = True

###################
# Defense - Green #
###################

@register_upgrade
class Defense1Upgrade(AddBuildingUpgrade):
    name = "b_defense1"
    resource_type = "iron"
    category = "buildings"
    title = "Reflector"
    description = "Gain a [^50] health reflector shield (does not regenerate)"
    icon = "reflectorshield"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':[]}
    building = ReflectorBuilding

@register_upgrade
class Defense2aUpgrade(AddBuildingUpgrade):
    name = "b_defense2a"
    resource_type = "iron"
    category = "buildings"
    title = "Resilient Ecosystem"
    description = "[^+100%] health and [^+5] health regeneration per second"
    icon = "resilientecosystem"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':['b_defense1']}
    building = make_simple_stats_building(stats=Stats(planet_health_mul=1, regen=2), shape="lifesupport")
    requires = ('b_defense1',)

@register_upgrade
class Defense2bUpgrade(AddBuildingUpgrade):
    name = "b_defense2b"
    resource_type = "iron"
    category = "buildings"
    title = "Armory"
    description = "When this planet takes damage, [!-1 pop], [^+1 fighter]. [!(10 second cooldown)]"
    icon = "armory"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':['b_defense1']}
    building = make_simple_stats_building(stats=Stats(armory=1), shape="lifesupport")
    requires = ('b_defense1',)

@register_upgrade
class Defense3Upgrade(AddBuildingUpgrade):
    name = "b_defense3"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Grants [^+20] health to nearby Ships"
    icon="loworbitdefenses"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':['b_defense2a', 'b_defense2b']}
    building = LowOrbitDefensesBuilding
    requires = lambda x:'b_defense1' in x and ('b_defense2a' in x or 'b_defense2b' in x)
    infinite = True    
    
#############
#### ICE ####
#############

# Dangerous - red
@register_upgrade
class Dangerous1Upgrade(AddBuildingUpgrade):
    name = "b_dangerous1"
    resource_type = "ice"
    category = "buildings"
    title = "SSM Battery"
    description = "Fire explosive missiles at nearby enemy ships"
    icon = "ssmbattery"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':[]}
    building = SSMBatteryBuilding

@register_upgrade
class Dangerous2aUpgrade(AddBuildingUpgrade):
    name = "b_dangerous2a"
    resource_type = "ice"
    category = "buildings"
    title = "Interplanetary SSM"
    description = "Fire explosive missiles at enemy ships and planets within 100 units"
    icon = "interplanetaryssm"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous1']}
    building = InterplanetarySSMBatteryBuilding
    requires = ('b_dangerous1',)

@register_upgrade
class Dangerous2bUpgrade(AddBuildingUpgrade):
    name = "b_dangerous2b"
    resource_type = "ice"
    category = "buildings"
    title = "Atmospheric EM Generator"
    description = "Enemy ships are disabled for 5 seconds the first time they move into range"
    icon = "emgenerator"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous1']}
    building = EMGeneratorBuilding
    requires = ('b_dangerous1',)

@register_upgrade
class Dangerous3Upgrade(AddBuildingUpgrade):
    name = "b_dangerous3"
    resource_type = "ice"
    category = "buildings"
    title = "Caustic Amplifier"
    description = "Planetary weapons deal [^+50%] damage"
    icon = "causticamplifier"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous2a', 'b_dangerous2b']}
    building = make_simple_stats_building(stats=Stats(planet_weapon_boost=0.5), shape="lifesupport")
    requires = lambda x:'b_dangerous1' in x and ('b_dangerous2a' in x or 'b_dangerous2b' in x)
    infinite = False

# Launchpad - Yellow
@register_upgrade
class Launchpad1Upgrade(AddBuildingUpgrade):
    name = "b_launchpad1"
    resource_type = "ice"
    category = "buildings"
    title = "Headquarters"
    description = "When a [Worker] sent from this planet colonizes a planet, [^+1] Population. [!30 second cooldown]"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(headquarters=1), shape="modulardwellings")

@register_upgrade
class Launchpad2aUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2a"
    resource_type = "ice"
    category = "buildings"
    title = "Employment Office"
    description = "If you are at maximum population, [^+40%] mining rate"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(mining_rate_at_max_pop=0.40), shape="lifesupport")
    requires = ('b_launchpad1',)

@register_upgrade
class Launchpad2bUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2b"
    resource_type = "ice"
    category = "buildings"
    title = "Workforce Housing"
    description = "[^+1] Max Population every 30 seconds; growth stops after 300 seconds or when you colonize a new planet"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(max_pop_growth=300), shape="lifesupport")
    requires = ('b_launchpad1',)

    def apply(self, to):
        to.owning_civ.housing_colonized = False
        return super().apply(to)

@register_upgrade
class Launchpad3Upgrade(AddBuildingUpgrade):
    name = "b_launchpad3"
    resource_type = "ice"
    category = "buildings"
    title = "Memorial"
    description = "When a ship sent from this planet dies, [^+1] [Fighter]. [!20 second cooldown]"    
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad2a', 'b_launchpad2b']}
    building = make_simple_stats_building(stats=Stats(memorial=1), shape="lifesupport")
    requires = lambda x:'b_launchpad1' in x and ('b_launchpad2a' in x or 'b_launchpad2b' in x)
    infinite = False    


# Scarcest - Brown
@register_upgrade
class Scarcest1Upgrade(AddBuildingUpgrade):
    name = "b_scarcest1"
    resource_type = "ice"
    category = "buildings"
    title = "Strip Mining"
    description = "[^+50%] faster [Ice] and [Gas] mining rate"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(ice_mining_rate=0.5, gas_mining_rate=0.5), shape="refinery")

@register_upgrade
class Scarcest2aUpgrade(AddBuildingUpgrade):
    name = "b_scarcest2a"
    resource_type = "ice"
    category = "buildings"
    title = "Cryosteel Alloy"
    description = "[^+5] [Ice] for every 10 [Iron] mined"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest1']}
    building = make_simple_stats_building(stats=Stats(mining_ice_per_iron=0.5), shape="lifesupport")
    requires = ('b_scarcest1',)

@register_upgrade
class Scarcest2bUpgrade(AddBuildingUpgrade):
    name = "b_scarcest2b"
    resource_type = "ice"
    category = "buildings"
    title = "Terraform"
    description = "Permanently flip iron and gas resource values on a planet"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest1']}
    building = make_simple_stats_building(stats=Stats(), shape="lifesupport")
    requires = ('b_scarcest1',)

    def apply(self, to):
        to.resources.gas, to.resources.iron = to.resources.iron, to.resources.gas
        to.regenerate_art()    
        return super().apply(to)

@register_upgrade
class Scarcest3Upgrade(AddBuildingUpgrade):
    name = "b_scarcest3"
    resource_type = "ice"
    category = "buildings"
    title = "Anodized Cryosteel"
    description = "[^+3] [Ice] and [^+2] [Gas] for every 10 [Iron] mined"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest2a', 'b_scarcest2b']}
    building = make_simple_stats_building(stats=Stats(mining_ice_per_iron = 0.3, mining_gas_per_iron = 0.2), shape="lifesupport")
    requires = lambda x:'b_scarcest1' in x and ('b_scarcest2a' in x or 'b_scarcest2b' in x)
    infinite = True  


#############
#### GAS ####
#############

# Ultra - Purple;


@register_upgrade
class Ultra1Upgrade(AddBuildingUpgrade):
    name = "b_ultra1"
    resource_type = "gas"
    category = "buildings"
    title = "Comm Station"
    description = "Enemy planets near the comm station reveal their ships and population when selected"
    icon = "clockwiseportal"
    cursor = ["allied_planet", "nearby"]
    family = {'tree':'ultra', 'parents':[]}
    building = building.CommStation
    requires = None

    def apply(self, to, pt):
        cso = CommStationObject(to.scene, pt)
        to.scene.game_group.add(cso)
        super().apply(to)

@register_upgrade
class Ultra2Upgrade(AddBuildingUpgrade):
    name = "b_ultra2"
    resource_type = "gas"
    category = "buildings"
    title = "Defense Matrix"
    description = "Produces a field that deals [^10%] of maximum health every second to enemy ships"
    icon = "defensematrixalpha"
    cursor = ["allied_planet", "nearby"]
    family = {'tree':'ultra', 'parents':['b_ultra1']}
    requires = ('b_ultra1',)
    building = building.DefenseMatrix

    def apply(self, to, pt):
        super().apply(to)
        dm = defensematrix.DefenseMatrix(to.scene, pt, to.owning_civ)
        to.scene.game_group.add(dm)
        b = [b for b in to.buildings if b['building'].upgrade == type(self)][0]
        b['building'].obj = dm

@register_upgrade
class Ultra3Upgrade(AddBuildingUpgrade):
    name = "b_ultra3"
    resource_type = "gas"
    category = "buildings"
    title = "Portal"
    description = "Portal allows teleportation between two allied planets"
    icon = "clockwiseportal"
    cursor = ["allied_planet", "allied_planet"]
    family = {'tree':'ultra', 'parents':['b_ultra2']}
    requires = ('b_ultra1','b_ultra2')
    building = building.Portal

    def apply(self, to, second):
        if to == second:
            return
        delta = (second.pos - to.pos).normalized()
        pos1 = to.pos + delta * (to.radius + 15)
        pos2 = second.pos - delta * (second.radius + 15)
        p1 = portal.Portal(to.scene, pos1, second, to.owning_civ)
        p2 = portal.Portal(to.scene, pos2, to, to.owning_civ)
        p1.other_portal = p2
        p2.other_portal = p1
        to.scene.game_group.add(p1)
        to.scene.game_group.add(p2)
        return super().apply(to)

# Deserted - Orange

@register_upgrade
class Deserted2bUpgrade(AddBuildingUpgrade):
    name = "b_deserted1"
    resource_type = "gas"
    category = "buildings"
    title = "Bunker Trap"
    description = "If this planet is razed, emit a [^20] damage shockwave. All buildings go underground and return if you re-take the planet"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(underground=1), shape="lifesupport")
    requires = None
    infinite = True

@register_upgrade
class Deserted2Upgrade(AddBuildingUpgrade):
    name = "b_deserted2"
    resource_type = "gas"
    category = "buildings"
    title = "Scrap Collector"
    description = "Whenever this planet takes damage, gain [^+5] [Iron]"
    icon = "building_default"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats = Stats(damage_iron=5), shape="modulardwellings")
    family = {'tree':'deserted', 'parents':['b_deserted1']}
    requires = ('b_deserted1',)

@register_upgrade
class Deserted3aUpgrade(AddBuildingUpgrade):
    name = "b_deserted3a"
    resource_type = "gas"
    category = "buildings"
    title = "War Economy A"
    description = "Produce [^1] [Fighter] every 45 seconds, [!-100% Max Population]"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted2']}
    requires = ('b_deserted1', 'b_deserted2')
    building = make_simple_stats_building(stats=Stats(pop_max_mul=-1), shape="modulardwellings")

    def apply(self, to):
        p = PermanentHangarProductionOrder(45)
        to.add_production(p)
        return super().apply(to)        

@register_upgrade
class Deserted3bUpgrade(AddBuildingUpgrade):
    name = "b_deserted3"
    resource_type = "gas"
    category = "buildings"
    title = "War Economy B"
    description = "Produce [^1] [Fighter] every 30 seconds, [!-90% Max Health]"
    icon = "building_default"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(planet_health_mul=-0.9), shape="lifesupport")
    family = {'tree':'deserted', 'parents':['b_deserted2']}
    requires = ('b_deserted1', 'b_deserted2')

    def apply(self, to):
        p = PermanentHangarProductionOrder(45)
        to.add_production(p)
        return super().apply(to)    

# Satellite - Black

@register_upgrade
class Satellite1Upgrade(AddBuildingUpgrade):
    name = "b_satellite1"
    resource_type = "gas"
    category = "buildings"
    title = "Space Station"
    description = "[^+4] maximum population"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':[]}
    building = SpaceStationBuilding

@register_upgrade
class Satellite2aUpgrade(AddBuildingUpgrade):
    name = "b_satellite2a"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Reflector"
    description = "Covers half the planet with a 50-health reflector shield; shield health regenerates at [^+2] health per second"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite1']}
    building = ReflectorShieldBuilding
    requires = ('b_satellite1',)


@register_upgrade
class Satellite2bUpgrade(AddBuildingUpgrade):
    name = "b_satellite2b"
    resource_type = "gas"
    category = "buildings"
    title = "Off-World Mining"
    description = "Gain [^+5] [Iron], [^+5] [Ice], and [^+5] [Gas] every 5 seconds."
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite1']}
    building = OffWorldMiningBuilding
    requires = ('b_satellite1',)   

@register_upgrade
class Satellite3Upgrade(AddBuildingUpgrade):
    name = "b_satellite3"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Laser"
    description = "Orbital Laser fires a constant beam at the nearest enemy target in line-of-sight"
    icon = "building_default"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite2a', 'b_satellite2b']}
    building = OrbitalLaserBuilding
    requires = lambda x:'b_satellite1' in x and ('b_satellite2a' in x or 'b_satellite2b' in x)
    infinite = True         


#################
# Unused        #
#################
class Health1Upgrade(AddBuildingUpgrade):
    name = "b_health1"
    resource_type = "iron"
    category = "buildings"
    title = "Planetary Defenses"
    description = "Planet has [^+50%] [Health] and [^+30] health per minute"
    icon="planetarydefenses"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(planet_health_mul=0.5, regen=0.5), shape="loworbitdefenses")
    family = {'tree':'planethealth', 'parents':[]}

class Health2AUpgrade(AddBuildingUpgrade):
    name = "b_health2a"
    resource_type = "iron"
    category = "buildings"
    title = "Repair Bay"
    description = "Planet Regenerates [^+2] health per second"
    icon="planetregen"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(regen=2), shape="repairbay")
    requires = ("b_health1",)
    family = {'tree':'planethealth', 'parents':['b_health1']}

class Health3Upgrade(AddBuildingUpgrade):
    name = "b_health3"
    resource_type = "iron"
    category = "buildings"
    title = "Planetary Shield"
    description = "Planet gains a [^150] health shield, which does not regenerate"
    icon="autoartillery"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(planet_shield=150), shape="autoartillery")
    requires = lambda x:'b_health1' in x and ('b_health2a' in x or 'b_health2b' in x)
    family = {'tree':'planethealth', 'parents':['b_health2a','b_health2b']}    
