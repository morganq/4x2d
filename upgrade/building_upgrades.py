from upgrade.upgrades import register_upgrade, Upgrade
from planet import building
from planet.building import *
from stats import Stats
import defensematrix
import portal
from planet import building as buildings

class AddBuildingUpgrade(Upgrade):
    building = None
    def apply(self, to):
        self.building.upgrade = type(self)
        to.add_building(self)

# Econ - light gray
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
    description = "[^+65%] [Mining Rate] for [Primary Resource], [!-2] [Max Population]"
    icon = "nuclearreactor"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.65, pop_max_add=-2), shape="nuclearreactor")
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

# Pop - skin color
@register_upgrade
class Pop1Upgrade(AddBuildingUpgrade):
    name = "b_pop1"
    resource_type = "iron"
    category = "buildings"
    title = "Modular Dwellings"
    description = "[^+33%] Maximum Population"
    icon = "modulardwellings"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(pop_max_mul=0.33), shape="modulardwellings")

@register_upgrade
class Pop2aUpgrade(AddBuildingUpgrade):
    name = "b_pop2a"
    resource_type = "iron"
    category = "buildings"
    title = "Life Support"
    description = "[^+2] Maximum Population"
    icon = "lifesupport"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="lifesupport")
    requires = ('b_pop1',)

@register_upgrade
class Pop2bUpgrade(AddBuildingUpgrade):
    name = "b_pop2b"
    resource_type = "iron"
    category = "buildings"
    title = "Armory"
    description = "For each [Population], planet fires [1] missile at nearby enemy ships"
    icon = "armory"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = buildings.ArmoryBuilding
    requires = ('b_pop1',)

@register_upgrade
class Pop3Upgrade(AddBuildingUpgrade):
    name = "b_pop3"
    resource_type = "iron"
    category = "buildings"
    title = "Underground Shelter"
    description = "[^+50%] population growth rate"
    icon = "undergroundshelter"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop2a', 'b_pop2b']}
    building = make_simple_stats_building(stats=Stats(pop_growth_rate=0.5), shape="undergroundshelter")
    requires = lambda x:'b_pop1' in x and ('b_pop2a' in x or 'b_pop2b' in x)
    infinite = True

# Health - dark green
@register_upgrade
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

@register_upgrade
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

@register_upgrade
class Health2BUpgrade(AddBuildingUpgrade):
    name = "b_health2b"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Grants [^+10] health to nearby Ships"
    icon="loworbitdefenses"
    cursor = "allied_planet"
    building = LowOrbitDefensesBuilding
    requires = ("b_health1",)  
    family = {'tree':'planethealth', 'parents':['b_health1']}

@register_upgrade
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

# Hangar - Pink
@register_upgrade
class Hangar1Upgrade(AddBuildingUpgrade):
    name = "b_hangar1"
    resource_type = "iron"
    category = "buildings"
    title = "Fighter Hangar"
    description = "[^+33%] [Fighter] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(fighter_production_amt=0.33), shape="modulardwellings")

@register_upgrade
class Hangar2aUpgrade(AddBuildingUpgrade):
    name = "b_hangar2a"
    resource_type = "iron"
    category = "buildings"
    title = "Interceptor Hangar"
    description = "[^+100%] [Interceptor] Production Quantity"
    icon = "mining"
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
    icon = "mining"
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
    description = "[^+50%] [Battleship] Production Speed"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar2a', 'b_hangar2b']}
    building = make_simple_stats_building(stats=Stats(battleship_production=0.5), shape="lifesupport")
    requires = lambda x:'b_hangar1' in x and ('b_hangar2a' in x or 'b_hangar2b' in x)
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
    description = "Fires missiles at nearby enemy ships"
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
    description = "Fires missiles at enemy ships and planets within 100 units"
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
    description = "Enemy ships are disabled for 3 seconds the first time they move into range"
    icon = "emgenerator"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous1']}
    building = EMGeneratorBuilding
    requires = ('b_dangerous1',)

@register_upgrade
class Dangerous3Upgrade(AddBuildingUpgrade):
    name = "b_dangerous3"
    resource_type = "iron"
    category = "buildings"
    title = "Caustic Amplifier"
    description = "If you have 0 population, planetary weapons deal +50% damage"
    icon = "causticamplifier"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous2a', 'b_dangerous2b']}
    building = make_simple_stats_building(stats=Stats(planet_weapon_boost_zero_pop=0.5), shape="lifesupport")
    requires = lambda x:'b_dangerous1' in x and ('b_dangerous2a' in x or 'b_dangerous2b' in x)
    infinite = False

# Launchpad - Yellow
@register_upgrade
class Launchpad1Upgrade(AddBuildingUpgrade):
    name = "b_launchpad1"
    resource_type = "ice"
    category = "buildings"
    title = "Headquarters"
    description = "50% chance to gain [^+1] population whenever you launch a colonist ship towards an enemy or neutral planet (20 second cooldown)"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(launchpad_pop_chance=0.5), shape="modulardwellings")

@register_upgrade
class Launchpad2aUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2a"
    resource_type = "ice"
    category = "buildings"
    title = "Employment Office"
    description = "If you are at maximum population, [^+40%] mining rate"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(mining_rate_at_max_pop=0.40), shape="lifesupport")
    requires = ('b_launchpad1',)

@register_upgrade
class Launchpad2bUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2b"
    resource_type = "ice"
    category = "buildings"
    title = "Launchpad"
    description = "33% chance for [^+1] [Fighter] whenever you launch an [Interceptor] or [Bomber] towards an enemy planet (10 second cooldown)"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(launchpad_fighter_chance=0.33), shape="lifesupport")
    requires = ('b_launchpad1',)

@register_upgrade
class Launchpad3Upgrade(AddBuildingUpgrade):
    name = "b_launchpad3"
    resource_type = "iron"
    category = "buildings"
    title = "Military Parade"
    description = "[^+1] population and [^+50] health restored whenever you launch a Battleship towards an enemy planet"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad2a', 'b_launchpad2b']}
    building = make_simple_stats_building(stats=Stats(launchpad_battleship_health=50,launchpad_battleship_pop=1), shape="lifesupport")
    requires = lambda x:'b_launchpad1' in x and ('b_launchpad2a' in x or 'b_launchpad2b' in x)
    infinite = False    


# Scarcest - Brown
@register_upgrade
class Scarcest1Upgrade(AddBuildingUpgrade):
    name = "b_scarcest1"
    resource_type = "ice"
    category = "buildings"
    title = "Strip Mining"
    description = "[^+50%] faster mining rate for the scarcest available resource"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(scarcest_mining_rate=0.50), shape="refinery")

@register_upgrade
class Scarcest2aUpgrade(AddBuildingUpgrade):
    name = "b_scarcest2a"
    resource_type = "ice"
    category = "buildings"
    title = "Cryosteel Alloy"
    description = "[^+5] [Ice] for every 10 [Iron] mined"
    icon = "mining"
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
    description = "Permanently invert planetary resources"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest1']}
    building = make_simple_stats_building(stats=Stats(), shape="lifesupport")
    requires = ('b_scarcest1',)

    def apply(self, to):
        # Invert resources impl
        return super().apply(to)

@register_upgrade
class Scarcest3Upgrade(AddBuildingUpgrade):
    name = "b_scarcest3"
    resource_type = "ice"
    category = "buildings"
    title = "Anodized Cryosteel"
    description = "[^+3] [Ice] and [^+2] [Gas] for every 10 [Iron] mined"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest2a', 'b_scarcest2b']}
    building = make_simple_stats_building(stats=Stats(mining_ice_per_iron = 0.3, mining_gas_per_iron = 0.2), shape="lifesupport")
    requires = lambda x:'b_scarcest1' in x and ('b_scarcest2a' in x or 'b_scarcest2b' in x)
    infinite = True  


#############
#### GAS ####
#############

# Ultra - Purple;
# defense matrix, portal (farthest?), 

@register_upgrade
class Ultra1Upgrade(AddBuildingUpgrade):
    name = "b_ultra1"
    resource_type = "gas"
    category = "buildings"
    title = "Defense Matrix"
    description = "Produces a field that deals [^10%] of maximum health every second to enemy ships"
    icon = "defensematrixalpha"
    cursor = ["allied_planet", "nearby"]
    family = {'tree':'ultra', 'parents':[]}
    building = building.DefenseMatrix

    def apply(self, to, pt):
        super().apply(to)
        dm = defensematrix.DefenseMatrix(to.scene, pt, to.owning_civ)
        to.scene.game_group.add(dm)
        b = [b for b in to.buildings if b['building'].upgrade == type(self)][0]
        b['building'].obj = dm

@register_upgrade
class Ultra2Upgrade(AddBuildingUpgrade):
    name = "b_ultra2"
    resource_type = "gas"
    category = "buildings"
    title = "Portal"
    description = "Portal allows teleportation between two allied planets"
    icon = "clockwiseportal"
    cursor = ["allied_planet", "allied_planet"]
    family = {'tree':'ultra', 'parents':['b_ultra1']}
    requires = ('b_ultra1',)
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

@register_upgrade
class Ultra3Upgrade(AddBuildingUpgrade):
    name = "b_ultra3"
    resource_type = "gas"
    category = "buildings"
    title = "Comm Station"
    description = "Enemy planets near the comm station reveal their ships and population when selected"
    icon = "clockwiseportal"
    cursor = ["allied_planet", "nearby"]
    family = {'tree':'ultra', 'parents':['b_ultra2']}
    building = building.CommStation
    requires = ('b_ultra1', 'b_ultra2')

    def apply(self, to, pt):
        cso = CommStationObject(to.scene, pt)
        to.scene.game_group.add(cso)
        super().apply(to)

# Deserted - Orange

@register_upgrade
class Deserted1Upgrade(AddBuildingUpgrade):
    name = "b_deserted1"
    resource_type = "gas"
    category = "buildings"
    title = "Organic Regeneration"
    description = "If there are no allied ships on or near the planet, gain [^+2] health per second"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(deserted_regen=2), shape="modulardwellings")

@register_upgrade
class Deserted2aUpgrade(AddBuildingUpgrade):
    name = "b_deserted2a"
    resource_type = "gas"
    category = "buildings"
    title = "Organic Regeneration II"
    description = "If there are no allied ships on or near the planet, gain [^+2] health per second"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted2']}
    building = make_simple_stats_building(stats=Stats(deserted_regen=2), shape="lifesupport")
    requires = ('b_deserted1',)

@register_upgrade
class Deserted2bUpgrade(AddBuildingUpgrade):
    name = "b_deserted2b"
    resource_type = "gas"
    category = "buildings"
    title = "Secret Bunker"
    description = "If this planet is lost, all buildings go underground; underground buildings return if you re-take the planet"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted1']}
    building = make_simple_stats_building(stats=Stats(underground=1), shape="lifesupport")
    requires = ('b_deserted1',)

@register_upgrade
class Deserted3Upgrade(AddBuildingUpgrade):
    name = "b_deserted3"
    resource_type = "gas"
    category = "buildings"
    title = "Munitions Recycling"
    description = "Whenever this planet takes damage, gain [^+5] [Iron]"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted2a', 'b_deserted2b']}
    building = make_simple_stats_building(stats=Stats(damage_iron=5), shape="lifesupport")
    requires = lambda x:'b_deserted1' in x and ('b_deserted2a' in x or 'b_deserted2b' in x)
    infinite = True

# Satellite - Black

@register_upgrade
class Satellite1Upgrade(AddBuildingUpgrade):
    name = "b_satellite1"
    resource_type = "gas"
    category = "buildings"
    title = "Space Station"
    description = "[^+4] maximum population"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':[]}
    building = SpaceStationBuilding

@register_upgrade
class Satellite2aUpgrade(AddBuildingUpgrade):
    name = "b_satellite2a"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Reflector"
    description = "Covers half the planet with a 50-health reflector shield; shield health regenerates at [^+1] health per second"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite2']}
    building = ReflectorShieldBuilding
    requires = ('b_satellite1',)


@register_upgrade
class Satellite2bUpgrade(AddBuildingUpgrade):
    name = "b_satellite2b"
    resource_type = "gas"
    category = "buildings"
    title = "Off-World Mining"
    description = "Gain [^+5] [Iron], [^+5] [Ice], and [^+5] [Gas] every 5 seconds."
    icon = "mining"
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
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite2a', 'b_satellite2b']}
    building = OrbitalLaserBuilding
    requires = lambda x:'b_satellite1' in x and ('b_satellite2a' in x or 'b_satellite2b' in x)
    infinite = True         