import random

import game
from stats import Stats

from upgrade.upgrades import Upgrade, register_upgrade


### 1) Mechanics: light grey ###
@register_upgrade
class Mechanics1Upgrade(Upgrade):
    name = "t_mechanics1"
    resource_type = "iron"
    category = "tech"
    title = "Precise Assembly"
    description = "[Fighters] gain [^+33%] rate of fire"
    icon = "preciseassembly"
    stats = Stats(fighter_fire_rate=0.33)
    family = {'tree':'t_mechanics', 'parents':[]}
    requires = None

@register_upgrade
class Mechanics2aUpgrade(Upgrade):
    name = "t_mechanics2a"
    resource_type = "iron"
    category = "tech"
    title = "Spaceport"
    description = "Planets with no docked ships gain [^+2] health per second and [^+33%] population growth rate"
    icon = "tech_default"
    stats = Stats(planet_regen_without_ships = 2, pop_growth_without_ships = 0.33)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

@register_upgrade
class Mechanics2bUpgrade(Upgrade):
    name = "t_mechanics2b"
    resource_type = "iron"
    category = "tech"
    title = "Material Reconstruction"
    description = "Gain [^+25] ice for each planet you control"
    icon = "matreconstruction"    
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            to.earn_resource("ice", 25, where=planet)
        return super().apply(to) 

@register_upgrade
class Mechanics3Upgrade(Upgrade):
    name = "t_mechanics3"
    resource_type = "iron"
    category = "tech"
    title = "Overgrowth"
    description = "Population grows [^+20%] faster for each docked ship"
    icon = "tech_default"
    stats = Stats(pop_growth_rate_per_docked_ship = 0.2)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics2a', 't_mechanics2b']}
    requires = lambda x: 't_mechanics1' in x and ('t_mechanics2a' in x or 't_mechanics2b' in x)
    infinite = True    

### 2) Atomic - Macro/Quick Tech: dark green
@register_upgrade
class Atomic1Upgrade(Upgrade):
    name = "t_atomic1"
    resource_type = "iron"
    category = "tech"
    title = "Nuclear Battery"
    description = "Each planet has [^+75%] mining rate for the first [60 seconds] after colonizing."
    icon = "nuclearbattery"
    stats = Stats(mining_rate_first_60=0.75)
    family = {'tree':'t_atomic', 'parents':[]}
    requires = None

@register_upgrade
class Atomic2aUpgrade(Upgrade):
    name = "t_atomic2a"
    resource_type = "iron"
    category = "tech"
    title = "Isotope Conversion"
    description = "Gain [150] [Ice] and [100] [Gas]. [Iron] is [!Frozen] for [20 seconds]."
    icon = "isotope"
    stats = Stats()
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)

    def apply(self, to):
        to.resources.ice += 150
        to.resources.gas += 100
        to.frozen.iron += 20
        return super().apply(to)

@register_upgrade
class Atomic2bUpgrade(Upgrade):
    name = "t_atomic2b"
    resource_type = "iron"
    category = "tech"
    title = "Atomic Assembler"
    description = "[^+50%] faster production of ships other than [Fighters]"
    icon = "atomicassembler"
    stats = Stats(bomber_production=0.50, interceptor_production=0.50, battleship_production=0.50)
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)

@register_upgrade
class Atomic3Upgrade(Upgrade):
    name = "t_atomic3"
    resource_type = "iron"
    category = "tech"
    title = "Unstable Reactor"
    description = "Mining rate on each planet slowly grows to [^+30%], but resets if attacked or if a ship is launched"
    icon = "unstablereactor"
    stats = Stats(unstable_reaction = 0.30)
    family = {'tree':'t_atomic', 'parents':['t_atomic2a', 't_atomic2b']}
    requires = lambda x: 't_atomic1' in x and ('t_atomic2a' in x or 't_atomic2b' in x)
    infinite = True

### 3) Vanguard
@register_upgrade
class Vanguard1Upgrade(Upgrade):
    name = "t_vanguard1"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Boosters"
    description = "Ships fly [^+50%] faster when targeting enemy planets"
    icon = "vanguardboosters"
    stats = Stats(ship_speed_mul_targeting_planets = 0.5)
    family = {'tree':'t_vanguard', 'parents':[]}
    requires = None

@register_upgrade
class Vanguard2aUpgrade(Upgrade):
    name = "t_vanguard2a"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Armor"
    description = "Ships gain a [^+10] health shield when far from a planet you control"
    icon = "vanguardarmor"
    stats = Stats(ship_shield_far_from_home = 10)
    family = {'tree':'t_vanguard', 'parents':['t_vanguard1']}
    requires = ('t_vanguard1',)

@register_upgrade
class Vanguard2bUpgrade(Upgrade):
    name = "t_vanguard2b"
    resource_type = "iron"
    category = "tech"
    title = "Warp Drive"
    description = "Ships gain warp drive: they can teleport forward [^+3] units in open space"
    icon = "warpdrive"
    stats = Stats(warp_drive = 3)
    family = {'tree':'t_vanguard', 'parents':['t_vanguard1']}
    requires = ('t_vanguard1',)
    infinite = True

@register_upgrade
class Vanguard3Upgrade(Upgrade):
    name = "t_vanguard3"
    resource_type = "iron"
    category = "tech"
    title = "Quantum Weirdness"
    description = "A [Worker] ship that uses warp drive has a [33% chance] for [^+1] population"
    icon = "quantumweirdness"
    stats = Stats(warp_drive_pop_chance=0.33)
    family = {'tree':'t_vanguard', 'parents':['t_vanguard2b']}
    requires = lambda x: 't_vanguard1' in x and 't_vanguard2b' in x
    infinite = False     


### 4) Quantum
@register_upgrade
class Quantum1Upgrade(Upgrade):
    name = "t_quantum1"
    resource_type = "iron"
    category = "tech"
    title = "Munitions Recycling"
    description = "When a [Fighter] deals damage to an enemy ship, gain [^+3] Iron"
    icon = "tech_default"
    stats = Stats(fighter_damage_iron = 3)
    family = {'tree':'t_quantum', 'parents':[]}
    requires = None

@register_upgrade
class Quantum2aUpgrade(Upgrade):
    name = "t_quantum2a"
    resource_type = "iron"
    category = "tech"
    title = "Proximity Alert"
    description = "Planets you control that are near enemy planets produce ships [^+100%] faster"
    icon = "tech_default"
    stats = Stats(ship_production_proximity=1)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)    

@register_upgrade
class Quantum2bUpgrade(Upgrade):
    name = "t_quantum2b"
    resource_type = "iron"
    category = "tech"
    title = "Nanothread Plating"
    description = "Ships have [^+25%] health"
    icon = "nanothread"
    stats = Stats(ship_health_mul = 0.25)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)

@register_upgrade
class Quantum3Upgrade(Upgrade):
    name = "t_quantum3"
    resource_type = "iron"
    category = "tech"
    title = "Grey Goo"
    description = "Fighter missiles apply Grey Goo on hit, inflicting damage over time to the target."
    icon = "tech_default"
    stats = Stats(grey_goo=1)
    family = {'tree':'t_quantum', 'parents':['t_quantum2a', 't_quantum2b']}
    requires = lambda x: 't_quantum1' in x and ('t_quantum2a' in x or 't_quantum2b' in x)
    infinite = False    

### 5) Crystal - Interceptor / contain: blue
@register_upgrade
class Crystal1Upgrade(Upgrade):
    name = "t_crystal1"
    resource_type = "ice"
    category = "tech"
    title = "Crystal Repeater"
    description = "[Interceptor] missiles bounce to hit a second target"
    icon = "resonancereloader"
    stats = Stats(interceptor_missile_bounce=1)
    family = {'tree':'t_crystal', 'parents':[]}
    requires = None

@register_upgrade
class Crystal2aUpgrade(Upgrade):
    name = "t_crystal2a"
    resource_type = "ice"
    category = "tech"
    title = "Phasing Lattice"
    description = "Ships near enemy planets have a [^+15%] chance to dodge missile weapons"
    icon = "phasinglattice"
    stats = Stats(ship_dodge_near_enemy_planets=0.15)
    family = {'tree':'t_crystal', 'parents':['t_crystal1']}
    requires = ('t_crystal1',)

@register_upgrade
class Crystal2bUpgrade(Upgrade):
    name = "t_crystal2b"
    resource_type = "ice"
    category = "tech"
    title = "Fragmentation Sequence"
    description = "If a [Worker] ship is destroyed, it explodes for [^20] damage. Radius is based on ship population"
    icon = "fragmentationsequence"
    stats = Stats(atomic_bomb=1)
    family = {'tree':'t_crystal', 'parents':['t_crystal1']}
    requires = ('t_crystal1',)

@register_upgrade
class Crystal3Upgrade(Upgrade):
    name = "t_crystal3"
    resource_type = "ice"
    category = "tech"
    title = "Crystal Repeater"
    description = "[Interceptors] gain a 10 health shield, and their missiles bounce to [^+1] target"
    icon = "crystalrepeater"
    stats = Stats(interceptor_shield=10, interceptor_missile_bounce=1)
    family = {'tree':'t_crystal', 'parents':['t_crystal2a', 't_crystal2b']}
    requires = lambda x: 't_crystal1' in x and ('t_crystal2a' in x or 't_crystal2b' in x)
    infinite = True

### 6) AI - green

@register_upgrade
class AI1Upgrade(Upgrade):
    name = "t_ai1"
    resource_type = "ice"
    category = "tech"
    title = "Orbital Targeting Solution"
    description = "Ships gain [^+66%] attack speed for [10 seconds] after take-off"
    icon = "orbitaltargeting"
    stats = Stats(ship_fire_rate_after_takeoff=0.66)
    family = {'tree':'t_ai', 'parents':[]}
    requires = None

@register_upgrade
class AI2aUpgrade(Upgrade):
    name = "t_ai2a"
    resource_type = "ice"
    category = "tech"
    title = "Artificial Intelligence"
    description = "Population growth rate [^+33%]. Population grows on planets even with [0] population"
    icon = "ai"
    stats = Stats(pop_growth_min_reduction=1, pop_growth_rate=0.33)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)

@register_upgrade
class AI2bUpgrade(Upgrade):
    name = "t_ai2b"
    resource_type = "ice"
    category = "tech"
    title = "Coordination Protocol"
    description = "[Interceptors] fire [^+50%] faster near [Bombers]"
    icon = "coordination"
    stats = Stats(interceptor_fire_rate_near_bombers=0.50)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)    
    infinite = True

@register_upgrade
class AI3Upgrade(Upgrade):
    name = "t_ai3"
    resource_type = "ice"
    category = "tech"
    title = "Robotic Assembly"
    description = "Whenever you gain control of a planet, [^add] a random tier 1 iron building"
    icon = "roboticassembly"
    stats = Stats(colonize_random_building=1)
    family = {'tree':'t_ai', 'parents':['t_ai2a', 't_ai2b']}
    requires = lambda x: 't_ai1' in x and ('t_ai2a' in x or 't_ai2b' in x)    

### 7) Proximity - Dark grey
@register_upgrade
class Proximity1Upgrade(Upgrade):
    name = "t_proximity1"
    resource_type = "ice"
    category = "tech"
    title = "Hostile Takeover"
    description = "A [Bomber] that helps raze a planet sends out a [Worker] ship to colonize it"
    icon = "tech_default"
    stats = Stats(bomber_colonist=1)
    family = {'tree':'t_proximity', 'parents':[]}
    requires = None

@register_upgrade
class Proximity1Upgrade(Upgrade):
    name = "t_proximity2a"
    resource_type = "ice"
    category = "tech"
    title = "Fire Bomb"
    description = "[Bombers] gain [^+25%] damage and have a [^30%] chance to destroy a random building on hit"
    icon = "tech_default"
    stats = Stats(bomber_raze_chance=0.3, bomber_damage_mul=0.25)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity2bUpgrade(Upgrade):
    name = "t_proximity2b"
    resource_type = "ice"
    category = "tech"
    title = "Space Mining"
    description = "Planets you control that are near hazards gain [^+33%] mining rate"
    icon = "tech_default"
    stats = Stats(mining_rate_proximity=.33)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity3Upgrade(Upgrade):
    name = "t_proximity3"
    resource_type = "ice"
    category = "tech"
    title = "Spoils"
    description = "When you raze a planet, gain [^1 full upgrade] of its primary resource"
    icon = "tech_default"
    stats = Stats(raze_upgrade=1)
    family = {'tree':'t_proximity', 'parents':['t_proximity2a', 't_proximity2b']}
    requires = lambda x: 't_proximity1' in x and ('t_proximity2a' in x or 't_proximity2b' in x)
    infinite = True

### 8) Optics - Black
@register_upgrade
class Optics1Upgrade(Upgrade):
    name = "t_optics1"
    resource_type = "gas"
    category = "tech"
    title = "Laser Diode"
    description = "[Battleships] rapidly fire lasers instead of missiles"
    icon = "tech_default"
    stats = Stats(battleship_laser=1)
    family = {'tree':'t_optics', 'parents':[]}
    requires = None

@register_upgrade
class Optics2aUpgrade(Upgrade):
    name = "t_optics2a"
    resource_type = "gas"
    category = "tech"
    title = "Fleet Upgrade"
    description = "[Battleships] gain [^+50%] health, other ships have [!-25%] health"
    icon = "tech_default"
    stats = Stats(ship_health_mul=-0.25, battleship_health_mul=0.75)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics2bUpgrade(Upgrade):
    name = "t_optics2b"
    resource_type = "gas"
    category = "tech"
    title = "Auto Focus"
    description = "Ships gradually gain attack speed while flying, up to [^+50%] over [60 seconds]"
    icon = "tech_default"
    stats = Stats(fire_rate_over_time=0.5)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics3Upgrade(Upgrade):
    name = "t_optics3"
    resource_type = "gas"
    category = "tech"
    title = "Refractor Shield"
    description = "Ships in a fleet of [8 or more] gain a [^20] damage shield"
    icon = "tech_default"
    stats = Stats(enclosure_shield=20)
    family = {'tree':'t_optics', 'parents':['t_optics2a', 't_optics2b']}
    requires = lambda x: 't_optics1' in x and ('t_optics2a' in x or 't_optics2b' in x)
    infinite = True


### 9) Exotic - variety: pink
@register_upgrade
class Exotic1Upgrade(Upgrade):
    name = "t_exotic1"
    resource_type = "gas"
    category = "tech"
    title = "Supercritical Materials"
    description = "Gain [^+200%] resources from asteroids"
    icon = "tech_default"
    stats = Stats(asteroid_yield_mul=2.0)
    family = {'tree':'t_exotic', 'parents':[]}
    requires = None


@register_upgrade
class Exotic2aUpgrade(Upgrade):
    name = "t_exotic2a"
    resource_type = "gas"
    category = "tech"
    title = "Transient Field"
    description = "Ships gain [^+10] health"
    icon = "tech_default"
    stats = Stats(ship_health_add=10)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

# TODO: replace
@register_upgrade
class Exotic2bUpgrade(Upgrade):
    name = "t_exotic2b"
    resource_type = "gas"
    category = "tech"
    title = "Gravitational Reinforcement"
    description = "Ships gain +35% fire rate"
    icon = "tech_default"
    stats = Stats(ship_fire_rate=0.35)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

@register_upgrade
class Exotic3Upgrade(Upgrade):
    name = "t_exotic3"
    resource_type = "gas"
    category = "tech"
    title = "Relativistic Targeting"
    description = "Ships gain [^+35%] attack range"
    icon = "tech_default"
    stats = Stats(ship_weapon_range=0.35)
    family = {'tree':'t_exotic', 'parents':['t_exotic2a', 't_exotic2b']}
    requires = lambda x: 't_exotic1' in x and ('t_exotic2a' in x or 't_exotic2b' in x)

### 10) Alien - yellow
@register_upgrade
class Alien1Upgrade(Upgrade):
    name = "t_alien1"
    resource_type = "gas"
    category = "tech"
    title = "Unknown Artifact"
    description = "Gain [^+3] re-rolls"
    icon = "tech_default"
    stats = Stats()
    family = {'tree':'t_alien', 'parents':[]}
    requires = None

    def apply(self, to):
        game.Game.inst.run_info.rerolls += 3
        return super().apply(to)

@register_upgrade
class Alien2aUpgrade(Upgrade):
    name = "t_alien2a"
    resource_type = "gas"
    category = "tech"
    title = "Alien Thrusters"
    description = "Ships move [^+33%] faster"
    icon = "tech_default"
    stats = Stats(ship_speed_mul=0.33)
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)

@register_upgrade
class Alien2bUpgrade(Upgrade):
    name = "t_alien2b"
    resource_type = "gas"
    category = "tech"
    title = "Kinetic Sling"
    description = "Ship weapons deal [^+50%] of bonus speed as bonus damage"
    icon = "tech_default"
    stats = Stats(ship_weapon_damage_speed=0.5)
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)

@register_upgrade
class Alien3Upgrade(Upgrade):
    name = "t_alien3"
    resource_type = "gas"
    category = "tech"
    title = "Alien Core Drill"
    description = "[^+30%] Ice mining and [^+15%] Gas mining"
    icon = "tech_default"
    stats = Stats(ice_mining_rate=0.3, gas_mining_rate=0.15)
    family = {'tree':'t_alien', 'parents':['t_alien2a', 't_alien2b']}
    requires = lambda x: 't_alien1' in x and ('t_alien2a' in x or 't_alien2b' in x)
    infinite = True


##########
# UNUSED #
##########

class Mechanics2aUpgrade(Upgrade):
    name = "t_mechanics2a"
    resource_type = "iron"
    category = "tech"
    title = "Decommission"
    description = "[!Destroy] 2 random [Fighters] you control. Gain [^5] population among random planets."
    icon = "decommission"
    stats = Stats()
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

    def apply(self, to):
        all_fighters = to.get_all_fighters()
        random.shuffle(all_fighters)
        for f in all_fighters[:2]:
            if f['type'] == 'ship':
                f['object'].kill()
            elif f['type'] == 'planet':
                f['object'].ships['fighter'] -= 1
                f['object'].needs_panel_update = True

        my_planets = to.scene.get_civ_planets(to)
        for i in range(5):
            random.choice(my_planets).population += 1

        return super().apply(to)

class Bio1Upgrade(Upgrade):
    name = "t_bio1"
    resource_type = "iron"
    category = "tech"
    title = "Symbiosis"
    description = "Planets gain [^+10] health per construction"
    icon = "tech_default"
    stats = Stats(planet_health_per_construct=10)
    family = {'tree':'t_bio', 'parents':[]}
    requires = None        
