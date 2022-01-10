import defensematrix
import portal
from planet import building
from planet import building as buildings
from planet.building import *
from productionorder import PermanentHangarProductionOrder
from stats import Stats

from upgrade.spacemine import SpaceMine
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
    description = "[^+50%] Mining Rate for primary resource"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'econ', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.5), shape="mine")

@register_upgrade
class Econ2AUpgrade(AddBuildingUpgrade):
    name = "b_econ2a"
    resource_type = "iron"
    category = "buildings"
    title = "Core Drill"
    description = "[^+100%] Mining Rate for primary resource, [!No more Buildings or Ships can be built here]"
    icon = "coredrill"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=1, prevent_buildings=1), shape="mine")
    requires = ("b_econ1",)
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ2BUpgrade(AddBuildingUpgrade):
    name = "b_econ2b"
    resource_type = "iron"
    category = "buildings"
    title = "Night Shift"
    description = "[^+50%] Mining Rate for primary resource, [!-50%] [Fighter] Production Quantity"
    icon = "nightshift"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.50, fighter_production_amt_halving=1), shape="mine")
    requires = ("b_econ1",)    
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ3Upgrade(AddBuildingUpgrade):
    name = "b_econ3"
    resource_type = "iron"
    category = "buildings"
    title = "IO Matrix"
    description = "[^+15%] Mining Rate for primary resource per building"
    icon = "iomatrix"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(top_mining_per_building=0.15), shape="mine")
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
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="habitat")

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
    building = make_simple_stats_building(stats=Stats(pop_max_mul=0.4), shape="habitat")
    requires = ('b_pop1',)

@register_upgrade
class Pop2bUpgrade(AddBuildingUpgrade):
    name = "b_pop2b"
    resource_type = "iron"
    category = "buildings"
    title = "Water Recycler"
    description = "Every 5 seconds, gain [^+2] [Ice] for each docked ship"
    icon = "waterrecycler"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = make_simple_stats_building(stats=Stats(ice_per_docked=2), shape="habitat")
    requires = ('b_pop1',)    

@register_upgrade
class Pop3Upgrade(AddBuildingUpgrade):
    name = "b_pop3"
    resource_type = "iron"
    category = "buildings"
    title = "Ground Crew"
    description = "Ships launched from this planet gain [^+10%] Speed and [^+5%] Attack Speed per [Worker]"
    icon = "groundcrew"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop2a', 'b_pop2b']}
    building = make_simple_stats_building(stats=Stats(ship_pop_boost=1), shape="habitat")
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
    title = "Basic Hangar"
    description = "[^+100%] [Fighter] and [Scout] Production Rate"
    icon = "fighterhangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(fighter_production=0.5, scout_production=0.5), shape="hangar")

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
    building = make_simple_stats_building(stats=Stats(interceptor_production=1), shape="hangar")
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
    building = make_simple_stats_building(stats=Stats(bomber_production=1), shape="hangar")
    requires = ('b_hangar1',)

@register_upgrade
class Hangar3Upgrade(AddBuildingUpgrade):
    name = "b_hangar3"
    resource_type = "iron"
    category = "buildings"
    title = "Battleship Hangar"
    description = "[^+150%] [Battleship] Production Rate"
    icon = "battleshiphangar"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar2a', 'b_hangar2b']}
    building = make_simple_stats_building(stats=Stats(battleship_production=1.5), shape="hangar")
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
    description = "[^+1] [Worker]. Gain a [Reflector Shield]"
    icon = "reflectorshield"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':[]}
    building = ReflectorBuilding

    def apply(self, to):
        super().apply(to)
        to.add_population(1)

@register_upgrade
class Defense2aUpgrade(AddBuildingUpgrade):
    name = "b_defense2a"
    resource_type = "iron"
    category = "buildings"
    title = "Resilient Ecosystem"
    description = "[^+2] [Workers]. [^+100%] Health and [^+5] Health Regeneration per second"
    icon = "resilientecosystem"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':['b_defense1']}
    building = make_simple_stats_building(stats=Stats(planet_health_mul=1, regen=5), shape="defenses")
    requires = ('b_defense1',)

    def apply(self, to):
        super().apply(to)
        to.add_population(2)

@register_upgrade
class Defense2bUpgrade(AddBuildingUpgrade):
    name = "b_defense2b"
    resource_type = "iron"
    category = "buildings"
    title = "Armory"
    description = "When this planet takes damage, [!-1] [Worker], [^+1] [Fighter]. 10 second cooldown"
    icon = "armory"
    cursor = "allied_planet"
    family = {'tree':'defense', 'parents':['b_defense1']}
    building = make_simple_stats_building(stats=Stats(armory=1), shape="defenses")
    requires = ('b_defense1',)

@register_upgrade
class Defense3Upgrade(AddBuildingUpgrade):
    name = "b_defense3"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Grants [^+20] Maximum Health to nearby ships"
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
    description = "Planet fires explosive missiles at nearby enemy ships"
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
    description = "Planet fires explosive missiles at enemy ships and planets within a large radius"
    icon = "interplanetaryssm"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous1']}
    building = InterplanetarySSMBatteryBuilding
    requires = ('b_dangerous1',)
    infinite = True

@register_upgrade
class Dangerous2bUpgrade(AddBuildingUpgrade):
    name = "b_dangerous2b"
    resource_type = "ice"
    category = "buildings"
    title = "Tesla Coil"
    description = "Enemy ships are [^stunned] for 5 seconds the first time they move into range"
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
    title = "Honeypot"
    description = "Enemy fighters that fly nearby are forced to target this planet"
    icon = "causticamplifier"
    cursor = "allied_planet"
    family = {'tree':'dangerous', 'parents':['b_dangerous2a', 'b_dangerous2b']}
    building = buildings.DecoyBuilding
    requires = lambda x:'b_dangerous1' in x and ('b_dangerous2a' in x or 'b_dangerous2b' in x)

# Launchpad - Yellow
@register_upgrade
class Launchpad1Upgrade(AddBuildingUpgrade):
    name = "b_launchpad1"
    resource_type = "ice"
    category = "buildings"
    title = "Ballistics Lab"
    description = "Ships you control in a large radius gain [^+4] Damage. Radius is reduced by the number of other planets you control."
    icon = "ballisticslab"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':[]}
    building = buildings.ScalingDamageAuraBuilding

@register_upgrade
class Launchpad2aUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2a"
    resource_type = "ice"
    category = "buildings"
    title = "Capitol"
    description = "[^+1] Max Population every 30 seconds. Growth stops after 300 seconds, or when you colonize a new planet"
    icon = "capitol"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(max_pop_growth=300), shape="capitol")
    requires = ('b_launchpad1',)

    def apply(self, to):
        to.owning_civ.housing_colonized = False
        return super().apply(to)

@register_upgrade
class Launchpad2bUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2b"
    resource_type = "ice"
    category = "buildings"
    title = "Memorial"
    description = "When a ship launched from this planet dies, [^+1] [Fighter]. 20 second cooldown"
    icon = "memorial"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building(stats=Stats(memorial=1), shape="memorial")
    requires = ('b_launchpad1',)

@register_upgrade
class Launchpad3Upgrade(AddBuildingUpgrade):
    name = "b_launchpad3"
    resource_type = "ice"
    category = "buildings"
    title = "Espionage Lab"
    description = "[Scouts] launched from this planet carry [^+2] [Disruptor Bombs]"
    icon = "espionagelab"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad2a', 'b_launchpad2b']}
    building = make_simple_stats_building(stats=Stats(scout_bombs=2), shape="lab")
    requires = lambda x:'b_launchpad1' in x and ('b_launchpad2a' in x or 'b_launchpad2b' in x)
    infinite = True


# Scarcest - Brown
@register_upgrade
class Scarcest1Upgrade(AddBuildingUpgrade):
    name = "b_scarcest1"
    resource_type = "ice"
    category = "buildings"
    title = "Cold Storage"
    description = "[^+50%] [Ice] and [Gas] Mining Rate"
    icon = "coldstorage"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(ice_mining_rate=0.5, gas_mining_rate=0.5), shape="terraform")

@register_upgrade
class Scarcest2aUpgrade(AddBuildingUpgrade):
    name = "b_scarcest2a"
    resource_type = "ice"
    category = "buildings"
    title = "Siphon"
    description = "Swap the resources of any two planets"
    icon = "siphon"
    cursor = ["any_planet", "any_planet"]
    family = {'tree':'scarcest', 'parents':['b_scarcest1']}
    building = make_simple_stats_building(stats=Stats(), shape="terraform")
    requires = ('b_scarcest1',)
    infinite = True

    def apply(self, to, second):
        to.resources, second.resources = second.resources, to.resources
        to.regenerate_art()
        second.regenerate_art()

@register_upgrade
class Scarcest2bUpgrade(AddBuildingUpgrade):
    name = "b_scarcest2b"
    resource_type = "ice"
    category = "buildings"
    title = "Terraform"
    description = "Permanently flip a planet's [Iron] and [Gas] resources"
    icon = "terraform"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest1']}
    building = make_simple_stats_building(stats=Stats(), shape="terraform")
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
    title = "Militarize"
    description = "[!Condemn this planet]. Your ships near this planet gain up to [^+100%] Speed based on planet's [Iron], up to [^+50%] Attack Speed based on planet's [Ice], and up to [^+100%] Maximum Health based on planet's [Gas]"
    icon = "militarize"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':['b_scarcest2a', 'b_scarcest2b']}
    building = MultiBonusAuraBuilding
    requires = lambda x:'b_scarcest1' in x and ('b_scarcest2a' in x or 'b_scarcest2b' in x)


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
    description = "Enemy planets near the [Comm Station] reveal their ships and workers when selected"
    icon = "commstation"
    cursor = ["allied_planet", "nearby"]
    family = {'tree':'ultra', 'parents':[]}
    building = building.CommStation
    requires = None

    def apply(self, to, pt):
        cso = CommStationObject(to.scene, pt)
        to.owning_civ.comm_objects.append(cso)
        to.scene.game_group.add(cso)
        super().apply(to)

@register_upgrade
class Ultra2aUpgrade(AddBuildingUpgrade):
    name = "b_ultra2a"
    resource_type = "gas"
    category = "buildings"
    title = "Defense Matrix"
    description = "Produces a field that deals [^10%] Maximum Health every second to enemy ships"
    icon = "defensivematrix"
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
class Ultra2bUpgrade(AddBuildingUpgrade):
    name = "b_ultra2b"
    resource_type = "gas"
    category = "buildings"
    title = "Portal"
    description = "Produces a portal that allows ship teleportation between two of your planets"
    icon = "clockwiseportal"
    cursor = ["allied_planet", "allied_planet"]
    family = {'tree':'ultra', 'parents':['b_ultra1']}
    requires = ('b_ultra1')
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
    title = "Proximity Mines"
    description = "Make a line of Mines between two of your planets"
    icon = "proximitymines"
    cursor = ["allied_planet", "allied_planet"]
    family = {'tree':'ultra', 'parents':['b_ultra2a', 'b_ultra2b']}
    requires = lambda x:'b_ultra1' in x and ('b_ultra2a' in x or 'b_ultra2b' in x)
    building = make_simple_stats_building(stats=Stats(), shape="ultra")

    def apply(self, to, second):
        if to == second:
            return False
            
        scene = to.scene
        if scene.flowfield.has_field(second):
            pass
        
        delta = second.pos - to.pos
        dn = delta.normalized()
        pos = to.pos + dn * (to.get_radius() + 10)
        i = 0
        while (pos - second.pos).sqr_magnitude() > (10 + second.get_radius()) ** 2:
            sm = SpaceMine(scene, pos, to.owning_civ, i / 9)
            scene.game_group.add(sm)
            step = scene.flowfield.get_vector(pos, second, 0) * 15
            pos += step
            i += 1
        
        return super().apply(to)

# Deserted - Orange

@register_upgrade
class Deserted2bUpgrade(AddBuildingUpgrade):
    name = "b_deserted1"
    resource_type = "gas"
    category = "buildings"
    title = "Bunker Trap"
    description = "If this planet is razed, emit a [^20] Damage shockwave. All your buildings go underground and return if you re-capture the planet"
    icon = "bunkertrap"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':[]}
    building = make_simple_stats_building(stats=Stats(underground=1), shape="bunkertrap")
    requires = None
    infinite = True

@register_upgrade
class Deserted2aUpgrade(AddBuildingUpgrade):
    name = "b_deserted2a"
    resource_type = "gas"
    category = "buildings"
    title = "Fighter Specialization"
    description = "[!Condemn this planet]. Produce [^1] [Fighter] every 45 seconds"
    icon = "fighterspecialization"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted1']}
    requires = ('b_deserted1',)
    building = make_simple_stats_building(stats=Stats(pop_max_mul=-1, prevent_buildings=1), shape="specialization")

    def apply(self, to):
        p = PermanentHangarProductionOrder("fighter", 45)
        to.add_production(p)
        return super().apply(to)    

@register_upgrade
class Deserted2bUpgrade(AddBuildingUpgrade):
    name = "b_deserted2b"
    resource_type = "gas"
    category = "buildings"
    title = "Scout Specialization"
    description = "[!Condemn this planet]. Produce [^1] [Scout] every 45 seconds"
    icon = "scoutspecialization"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats = Stats(pop_max_mul=-1, prevent_buildings=1), shape="specialization")
    family = {'tree':'deserted', 'parents':['b_deserted1']}
    requires = ('b_deserted1',)    

    def apply(self, to):
        p = PermanentHangarProductionOrder("scout", 45)
        to.add_production(p)
        return super().apply(to)        

@register_upgrade
class Deserted3Upgrade(AddBuildingUpgrade):
    name = "b_deserted3"
    resource_type = "gas"
    category = "buildings"
    title = "Self-Destruct"
    description = "In 30 seconds, this planet [!explodes], dealing [^100] Damage to enemy ships and planets in a large radius"
    icon = "selfdestruct"
    cursor = "allied_planet"
    building = make_simple_stats_building(stats=Stats(planet_self_destruct=1), shape="selfdestruct")
    family = {'tree':'deserted', 'parents':['b_deserted2a', 'b_deserted2b']}
    requires = lambda x:'b_deserted1' in x and ('b_deserted2a' in x or 'b_deserted2b' in x)

# Satellite - Black

@register_upgrade
class Satellite1Upgrade(AddBuildingUpgrade):
    name = "b_satellite1"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Habitat"
    description = "[^+4] Maximum Population"
    icon = "orbitalhabitat"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':[]}
    building = SpaceStationBuilding

@register_upgrade
class Satellite2aUpgrade(AddBuildingUpgrade):
    name = "b_satellite2a"
    resource_type = "gas"
    category = "buildings"
    title = "Air Compressor"
    description = "[^+3] [Oxygen] every 10 seconds"
    icon = "aircompressor"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite1']}
    building = OxygenBuilding
    requires = ('b_satellite1',)


@register_upgrade
class Satellite2bUpgrade(AddBuildingUpgrade):
    name = "b_satellite2b"
    resource_type = "gas"
    category = "buildings"
    title = "Space Junk Collector"
    description = "[^+5% of maximum] [Iron] every 10 seconds"
    icon = "spacejunk"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite1']}
    building = OffWorldMiningBuilding
    requires = ('b_satellite1',)   
    infinite = True

@register_upgrade
class Satellite3Upgrade(AddBuildingUpgrade):
    name = "b_satellite3"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Laser"
    description = "Creates an Orbital Laser which fires a constant beam at the nearest enemy target in line-of-sight"
    icon = "orbitallaser"
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

class Pop2bUpgrade(AddBuildingUpgrade):
    name = "b_pop2b"
    resource_type = "iron"
    category = "buildings"
    title = "University"
    description = "Ship production is [^+15%] faster for each population"
    icon = "university"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop1']}
    building = make_simple_stats_building(stats=Stats(ship_production_rate_per_pop=0.15), shape="lifesupport")
    requires = ('b_pop1',)
