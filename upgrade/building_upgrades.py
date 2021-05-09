from upgrade.upgrades import register_upgrade, Upgrade
from planet import building
from planet.building import make_simple_stats_building
from stats import Stats

class AddBuildingUpgrade(Upgrade):
    building = None
    def apply(self, to):
        b = to.add_building(self.building)
        b.upgrade = self.name

# Econ - light gray
@register_upgrade
class EconUpgrade(AddBuildingUpgrade):
    name = "b_econ1"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+25%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'econ', 'parents':[]}
    building = make_simple_stats_building("b_econ1", stats=Stats(top_mining_rate=0.25), shape="refinery")

@register_upgrade
class Econ2AUpgrade(AddBuildingUpgrade):
    name = "b_econ2a"
    resource_type = "iron"
    category = "buildings"
    title = "Nuclear Reactor"
    description = "[^+50%] [Mining Rate] for [Primary Resource], [!-2] [Max Population]"
    icon = "nuclearreactor"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_econ2a", stats=Stats(top_mining_rate=0.5, pop_max_add=-2), shape="nuclearreactor")
    requires = ("b_econ1",)
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ2BUpgrade(AddBuildingUpgrade):
    name = "b_econ2b"
    resource_type = "iron"
    category = "buildings"
    title = "Military Surplus"
    description = "[^+25%] [Mining Rate] for [Primary Resource], [!-50%] [Fighter Production]"
    icon = "militarysurplus"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_econ2b", stats=Stats(top_mining_rate=0.25, fighter_production_amt_halving=1), shape="militarysurplus")
    requires = ("b_econ1",)    
    family = {'tree':'econ', 'parents':['b_econ1']}

@register_upgrade
class Econ3Upgrade(AddBuildingUpgrade):
    name = "b_econ3"
    resource_type = "iron"
    category = "buildings"
    title = "IO Matrix"
    description = "[^+10%] [Mining Rate] for [Primary Resource] per Building"
    icon = "iomatrix"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_econ3", stats=Stats(top_mining_per_building=0.1), shape="iomatrix")
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
    building = make_simple_stats_building("b_pop1", stats=Stats(pop_max_mul=0.33), shape="modulardwellings")

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
    building = make_simple_stats_building("b_pop1", stats=Stats(pop_max_add=2), shape="lifesupport")
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
    building = "pop2b"
    requires = ('b_pop1',)

@register_upgrade
class Pop3Upgrade(AddBuildingUpgrade):
    name = "b_pop3"
    resource_type = "iron"
    category = "buildings"
    title = "Underground Shelter"
    description = "[^+25%] [Max Population], [!-50%] [Max Health]"
    icon = "undergroundshelter"
    cursor = "allied_planet"
    family = {'tree':'pop', 'parents':['b_pop2a', 'b_pop2b']}
    building = make_simple_stats_building("b_pop3", stats=Stats(pop_max_mul=0.25, planet_health_mul=-0.50), shape="undergroundshelter")
    requires = lambda x:'b_pop1' in x and ('b_pop2a' in x or 'b_pop2b' in x)
    infinite = True

# Health - dark green
@register_upgrade
class Health1Upgrade(AddBuildingUpgrade):
    name = "b_health1"
    resource_type = "iron"
    category = "buildings"
    title = "Planetary Defenses"
    description = "Planet has [^+50%] [Health]"
    icon="planetarydefenses"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_health1", stats=Stats(planet_health_mul=0.5), shape="loworbitdefenses")
    family = {'tree':'planethealth', 'parents':[]}

@register_upgrade
class Health2AUpgrade(AddBuildingUpgrade):
    name = "b_health2a"
    resource_type = "iron"
    category = "buildings"
    title = "Repair Bay"
    description = "Planet Regenerates [^+1] [Health/Sec]"
    icon="planetregen"
    cursor = "allied_planet"
    building = "health2a"
    requires = ("b_health1",)
    family = {'tree':'planethealth', 'parents':['b_health1']}

@register_upgrade
class Health2BUpgrade(AddBuildingUpgrade):
    name = "b_health2b"
    resource_type = "iron"
    category = "buildings"
    title = "Low Orbit Defenses"
    description = "Grants [^+10] [Health] to Nearby Ships"
    icon="loworbitdefenses"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_health2b", stats=Stats(planet_health_aura=10), shape="highorbitdefenses")
    requires = ("b_health1",)  
    family = {'tree':'planethealth', 'parents':['b_health1']}

@register_upgrade
class Health3Upgrade(AddBuildingUpgrade):
    name = "b_health3"
    resource_type = "iron"
    category = "buildings"
    title = "Auto Artillery"
    description = "When Hit, Planet Fires Back"
    icon="autoartillery"
    cursor = "allied_planet"
    building = make_simple_stats_building("b_health3", stats=Stats(planet_thorns=1), shape="autoartillery")
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
    building = make_simple_stats_building("b_hangar1", stats=Stats(fighter_production_amt=0.33), shape="modulardwellings")

@register_upgrade
class Hangar2aUpgrade(AddBuildingUpgrade):
    name = "b_hangar2a"
    resource_type = "iron"
    category = "buildings"
    title = "Interceptor Hangar"
    description = "Unlock Interceptors. [^+50%] [Interceptor] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar1']}
    building = make_simple_stats_building("b_hangar2a", stats=Stats(interceptor_production=0.5), shape="lifesupport")
    requires = ('b_hangar1',)

@register_upgrade
class Hangar2bUpgrade(AddBuildingUpgrade):
    name = "b_hangar2b"
    resource_type = "iron"
    category = "buildings"
    title = "Bomber Hangar"
    description = "Unlock Bombers. [^+50%] [Bomber] Production Quantity"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar1']}
    building = make_simple_stats_building("b_hangar2b", stats=Stats(bomber_production=0.5), shape="lifesupport")
    requires = ('b_hangar1',)

@register_upgrade
class Hangar3Upgrade(AddBuildingUpgrade):
    name = "b_hangar3"
    resource_type = "iron"
    category = "buildings"
    title = "Battleship Hangar"
    description = "Unlock Battleships. [^+10%] [Battleship] Production Speed"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_hangar2a', 'b_hangar2b']}
    building = make_simple_stats_building("b_hangar3", stats=Stats(battleship_production=0.5), shape="lifesupport")
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
    building = make_simple_stats_building("b_dangerous1", stats=Stats(surface_space_missiles=1), shape="modulardwellings")

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
    building = make_simple_stats_building("b_dangerous2a", stats=Stats(interplanetary_missiles=1), shape="lifesupport")
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
    building = make_simple_stats_building("b_dangerous2b", stats=Stats(stun_nearby_ships=3), shape="lifesupport")
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
    building = make_simple_stats_building("b_dangerous3", stats=Stats(planet_weapon_boost_zero_pop=0.5), shape="lifesupport")
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
    building = make_simple_stats_building("b_launchpad1", stats=Stats(launchpad_pop_chance=0.5), shape="modulardwellings")

@register_upgrade
class Launchpad2aUpgrade(AddBuildingUpgrade):
    name = "b_launchpad2a"
    resource_type = "ice"
    category = "buildings"
    title = "Employment Office"
    description = "If you are at maximum population, [^+25%] mining rate"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'launchpad', 'parents':['b_launchpad1']}
    building = make_simple_stats_building("b_launchpad2a", stats=Stats(mining_rate_at_max_pop=0.25), shape="lifesupport")
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
    building = make_simple_stats_building("b_launchpad2b", stats=Stats(launchpad_fighter_chance=0.33), shape="lifesupport")
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
    building = make_simple_stats_building("b_launchpad3", stats=Stats(launchpad_battleship_health=50,launchpad_battleship_pop=1), shape="lifesupport")
    requires = lambda x:'b_launchpad1' in x and ('b_launchpad2a' in x or 'b_launchpad2b' in x)
    infinite = False    


# Scarcest - Brown
@register_upgrade
class Scarcest1Upgrade(AddBuildingUpgrade):
    name = "b_scarcest1"
    resource_type = "ice"
    category = "buildings"
    title = "Strip Mining"
    description = "[^+25%] faster mining rate for the scarcest available resource"
    icon = "refinery"
    cursor = "allied_planet"
    family = {'tree':'scarcest', 'parents':[]}
    building = make_simple_stats_building("b_scarcest1", stats=Stats(scarcest_mining_rate=0.25), shape="refinery")

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
    building = make_simple_stats_building("b_scarcest2a", stats=Stats(mining_ice_per_iron=0.5), shape="lifesupport")
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
    building = make_simple_stats_building("b_scarcest2b", stats=Stats(), shape="lifesupport")
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
    building = make_simple_stats_building("b_scarcest3", stats=Stats(mining_ice_per_iron = 0.3, mining_gas_per_iron = 0.2), shape="lifesupport")
    requires = lambda x:'b_scarcest1' in x and ('b_scarcest2a' in x or 'b_scarcest2b' in x)
    infinite = True  


#############
#### GAS ####
#############

# Ultra - Purple

@register_upgrade
class Ultra1Upgrade(AddBuildingUpgrade):
    name = "b_ultra1"
    resource_type = "gas"
    category = "buildings"
    title = "Defense Matrix Alpha"
    description = "When constructed on a different planet from Defense Matrix Omega, produces an inter-planetary field that damages enemy ships"
    icon = "defensematrixalpha"
    cursor = "allied_planet"
    family = {'tree':'ultra', 'parents':[]}
    building = building.DefenseMatrixAlpha

@register_upgrade
class Ultra2Upgrade(AddBuildingUpgrade):
    name = "b_ultra2"
    resource_type = "gas"
    category = "buildings"
    title = "Defense Matrix Omega"
    description = "When constructed on a different planet from Defense Matrix Alpha, produces an inter-planetary field that damages enemy ships"
    icon = "defensematrixomega"
    cursor = "allied_planet"
    family = {'tree':'ultra', 'parents':['b_ultra1']}
    requires = ('b_ultra1',)
    building = building.DefenseMatrixOmega

@register_upgrade
class Ultra3aUpgrade(AddBuildingUpgrade):
    name = "b_ultra3a"
    resource_type = "gas"
    category = "buildings"
    title = "Clockwise Portal"
    description = "When constructed on a different planet from Counter-Clockwise Portal, produces a portal that allows instantaneous travel"
    icon = "clockwiseportal"
    cursor = "allied_planet"
    family = {'tree':'ultra', 'parents':['b_ultra2']}
    building = building.ClockwisePortal
    requires = ('b_ultra1', 'b_ultra2')

@register_upgrade
class Ultra3bUpgrade(AddBuildingUpgrade):
    name = "b_ultra3b"
    resource_type = "gas"
    category = "buildings"
    title = "Counter-Clockwise Portal"
    description = "When constructed on a different planet from Clockwise Portal, produces a portal that allows instantaneous travel"
    icon = "counterclockwiseportal"
    cursor = "allied_planet"
    family = {'tree':'ultra', 'parents':['b_ultra2']}
    building = building.ClockwisePortal
    requires = ('b_ultra1', 'b_ultra2') 

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
    building = make_simple_stats_building("b_deserted1", stats=Stats(deserted_regen=2), shape="modulardwellings")

@register_upgrade
class Deserted2aUpgrade(AddBuildingUpgrade):
    name = "b_deserted2a"
    resource_type = "gas"
    category = "buildings"
    title = "Organic Regeneration II"
    description = "If there are no allied ships on or near the planet, gain [^+2] health per second"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_deserted2']}
    building = make_simple_stats_building("b_deserted2a", stats=Stats(deserted_regen=2), shape="lifesupport")
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
    building = make_simple_stats_building("b_deserted2b", stats=Stats(underground=1), shape="lifesupport")
    requires = ('b_deserted1',)

@register_upgrade
class Deserted3Upgrade(AddBuildingUpgrade):
    name = "b_deserted3"
    resource_type = "gas"
    category = "buildings"
    title = ""
    description = "Whenever this planet takes damage, gain [^+5] [Iron]"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'deserted', 'parents':['b_deserted2a', 'b_deserted2b']}
    building = make_simple_stats_building("b_deserted3", stats=Stats(damage_iron=5), shape="lifesupport")
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
    building = make_simple_stats_building("b_satellite1", stats=Stats(pop_max_add=4), shape="modulardwellings")

    def apply(self, to):
        # impl make space station
        return super().apply(to)

@register_upgrade
class Satellite2aUpgrade(AddBuildingUpgrade):
    name = "b_satellite2a"
    resource_type = "gas"
    category = "buildings"
    title = "Orbital Reflector"
    description = "Covers half the planet with a 50-health reflector shield; shield health regenerates at [^+2] health per second"
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'hangar', 'parents':['b_satellite2']}
    building = make_simple_stats_building("b_satellite2a", stats=Stats(), shape="lifesupport")
    requires = ('b_satellite1',)

    def apply(self, to):
        # impl make satellite
        return super().apply(to)    

@register_upgrade
class Satellite2bUpgrade(AddBuildingUpgrade):
    name = "b_satellite2b"
    resource_type = "gas"
    category = "buildings"
    title = "Off-World Mining"
    description = "Gain [^+5] [Iron], [^+5] [Ice], and [^+5] [Gas] every 10 seconds."
    icon = "mining"
    cursor = "allied_planet"
    family = {'tree':'satellite', 'parents':['b_satellite1']}
    building = make_simple_stats_building("b_satellite2b", stats=Stats(), shape="lifesupport")
    requires = ('b_satellite1',)

    def apply(self, to):
        # impl make satellite
        return super().apply(to)       

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
    building = make_simple_stats_building("b_satellite3", stats=Stats(), shape="lifesupport")
    requires = lambda x:'b_satellite1' in x and ('b_satellite2a' in x or 'b_satellite2b' in x)
    infinite = True    

    def apply(self, to):
        # impl make satellite
        return super().apply(to)         