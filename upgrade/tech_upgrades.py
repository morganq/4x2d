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
    description = "[Fighters] gain [^+33%] Attack Speed"
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
    description = "Planets with no docked ships gain [^+2] Health per second and [^+33%] Population Growth Rate"
    icon = "spaceports"
    stats = Stats(planet_regen_without_ships = 2, pop_growth_without_ships = 0.33)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

@register_upgrade
class Mechanics2bUpgrade(Upgrade):
    name = "t_mechanics2b"
    resource_type = "iron"
    category = "tech"
    title = "Overflow Tanks"
    description = "Gain [^+25] [Ice] for each planet you control"
    icon = "overflowtanks"    
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)
    infinite = True

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            to.earn_resource("ice", 25, where=planet)
        return super().apply(to) 

@register_upgrade
class Mechanics3Upgrade(Upgrade):
    name = "t_mechanics3"
    resource_type = "iron"
    category = "tech"
    title = "Turbocharger"
    description = "Ships gain [^+33%] Speed and [^+33%] Attack Speed. Every time you issue an order to a fleet, [!-5] Oyxgen"
    icon = "turbocharger"
    stats = Stats(ship_speed_mul = 0.33, ship_fire_rate = 0.33)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics2a', 't_mechanics2b']}
    requires = lambda x: 't_mechanics1' in x and ('t_mechanics2a' in x or 't_mechanics2b' in x)

    def apply(self, to):
        # TODO: impl in multiplayer
        to.oxygen_cost_per_order += 5
        return super().apply(to)

### 2) Atomic - Macro/Quick Tech: dark green
@register_upgrade
class Atomic1Upgrade(Upgrade):
    name = "t_atomic1"
    resource_type = "iron"
    category = "tech"
    title = "Nuclear Battery"
    description = "Each planet has [^+100%] Mining Rate for the first 120 seconds after capture."
    icon = "nuclearbattery"
    stats = Stats(mining_rate_first_120=1)
    family = {'tree':'t_atomic', 'parents':[]}
    requires = None

@register_upgrade
class Atomic2aUpgrade(Upgrade):
    name = "t_atomic2a"
    resource_type = "iron"
    category = "tech"
    title = "Isotope Conversion"
    description = "Gain [+50% of Maximum] [Ice] and [+50% of Maximum] [Gas]."
    icon = "isotope"
    stats = Stats()
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)
    infinite = True

    def apply(self, to):
        to.resources.ice += to.upgrade_limits.ice * 0.5
        to.resources.gas += to.upgrade_limits.gas * 0.5
        return super().apply(to)

@register_upgrade
class Atomic2bUpgrade(Upgrade):
    name = "t_atomic2b"
    resource_type = "iron"
    category = "tech"
    title = "Atomic Assembler"
    description = "[^+50%] Production Rate of ships other than [Fighters]"
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
    description = "[^+30%] Mining Rate on each planet. [!Lose this bonus] for 60 seconds if the planet is attacked or launches a ship"
    icon = "unstablereactor"
    stats = Stats(unstable_reaction = 0.30)
    family = {'tree':'t_atomic', 'parents':['t_atomic2a', 't_atomic2b']}
    requires = lambda x: 't_atomic1' in x and ('t_atomic2a' in x or 't_atomic2b' in x)

### 3) Vanguard
@register_upgrade
class Vanguard1Upgrade(Upgrade):
    name = "t_vanguard1"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Boosters"
    description = "Ships have [^+50%] Speed when targeting neutral or enemy planets"
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
    description = "Ships have [^+10] Shield when far from a planet you control"
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
    description = "Ships can warp forward [^+3] units in open space"
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
    description = "A [Worker Ship] that uses Warp Drive has a [33% chance] to gain [^+3] Population"
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
    description = "When a [Fighter] deals damage to an enemy ship, gain [^+3] [Iron]"
    icon = "munitionsrecycling"
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
    icon = "proximityalert"
    stats = Stats(ship_production_proximity=1)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)    

@register_upgrade
class Quantum2bUpgrade(Upgrade):
    name = "t_quantum2b"
    resource_type = "iron"
    category = "tech"
    title = "Nanothread Plating"
    description = "Ships have [^+20%] Health"
    icon = "nanothread"
    stats = Stats(ship_health_mul = 0.25)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)
    infinite = True

@register_upgrade
class Quantum3Upgrade(Upgrade):
    name = "t_quantum3"
    resource_type = "iron"
    category = "tech"
    title = "Grey Goo"
    description = "Scouts apply Grey Goo, inflicting damage over time to the target"
    icon = "greygoo"
    stats = Stats(grey_goo=1)
    family = {'tree':'t_quantum', 'parents':['t_quantum2a', 't_quantum2b']}
    requires = lambda x: 't_quantum1' in x and ('t_quantum2a' in x or 't_quantum2b' in x)

### 5) Crystal - Interceptor / contain: blue
@register_upgrade
class Crystal1Upgrade(Upgrade):
    name = "t_crystal1"
    resource_type = "ice"
    category = "tech"
    title = "Crystal Repeater"
    description = "[Interceptor] missiles bounce to hit an additional target"
    icon = "crystalrepeater"
    stats = Stats(interceptor_missile_bounce=1)
    family = {'tree':'t_crystal', 'parents':[]}
    requires = None

@register_upgrade
class Crystal2aUpgrade(Upgrade):
    name = "t_crystal2a"
    resource_type = "ice"
    category = "tech"
    title = "Phasing Lattice"
    description = "[Bombers] dodge the first 3 attacks that target them"
    icon = "phasinglattice"
    stats = Stats(bomber_dodge_num=3)
    family = {'tree':'t_crystal', 'parents':['t_crystal1']}
    requires = ('t_crystal1',)

@register_upgrade
class Crystal2bUpgrade(Upgrade):
    name = "t_crystal2b"
    resource_type = "ice"
    category = "tech"
    title = "Fragmentation Sequence"
    description = "If a [Worker] ship is destroyed, it explodes for [^5] Damage. Damage and radius increase with ship Population"
    icon = "fragmentationsequence"
    stats = Stats(atomic_bomb=1)
    family = {'tree':'t_crystal', 'parents':['t_crystal1']}
    requires = ('t_crystal1',)

@register_upgrade
class Crystal3Upgrade(Upgrade):
    name = "t_crystal3"
    resource_type = "ice"
    category = "tech"
    title = "Crystal Repeater II"
    description = "[Interceptors] gain [^+10] Shield, and their missiles bounce to [^+1] target"
    icon = "crystalrepeater2"
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
    description = "Ships gain [^+50%] Attack Speed for 5 seconds after take-off"
    icon = "orbitaltargeting"
    stats = Stats(ship_fire_rate_after_takeoff=0.5)
    family = {'tree':'t_ai', 'parents':[]}
    requires = None

@register_upgrade
class AI2aUpgrade(Upgrade):
    name = "t_ai2a"
    resource_type = "ice"
    category = "tech"
    title = "Artificial Intelligence"
    description = "[^+33%] Population Growth Rate. Population grows on planets even with 0 [Workers]"
    icon = "ai"
    stats = Stats(pop_growth_min_reduction=1, pop_growth_rate=0.33)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)

@register_upgrade
class AI2bUpgrade(Upgrade):
    name = "t_ai2b"
    resource_type = "ice"
    category = "tech"
    title = "Smart Rounds"
    description = "Ships gain [^+2] Damage"
    icon = "smartrounds"
    stats = Stats(ship_weapon_damage=2)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)    
    infinite = True

@register_upgrade
class AI3Upgrade(Upgrade):
    name = "t_ai3"
    resource_type = "ice"
    category = "tech"
    title = "Robotic Assembly"
    description = "Whenever you capture a planet, [^add] a random Tier 1 [Iron] Building"
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
    description = "A [Bomber] that helps raze a planet sends out a [Worker] ship to capture it"
    icon = "extremehabitat"
    stats = Stats(bomber_colonist=1)
    family = {'tree':'t_proximity', 'parents':[]}
    requires = None

@register_upgrade
class Proximity1Upgrade(Upgrade):
    name = "t_proximity2a"
    resource_type = "ice"
    category = "tech"
    title = "Fire Bomb"
    description = "[Bombers] gain [^+25%] Damage and have a [^30%] chance to destroy a random building on hit"
    icon = "firebomb"
    stats = Stats(bomber_raze_chance=0.3, bomber_damage_mul=0.25)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity2bUpgrade(Upgrade):
    name = "t_proximity2b"
    resource_type = "ice"
    category = "tech"
    title = "Thermal Dissipator"
    description = "Ships gain +1 armor"
    icon = "thermaldissipator"
    stats = Stats(ship_armor=1)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity3Upgrade(Upgrade):
    name = "t_proximity3"
    resource_type = "ice"
    category = "tech"
    title = "Explosive Extraction"
    description = "When you raze a planet, gain [^1 full upgrade] of its primary resource"
    icon = "explosiveextraction"
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
    description = "[Battleship] weapon upgrade - rapid laser array replaces missile weapon"
    icon = "laserdiode"
    stats = Stats(battleship_laser=1)
    family = {'tree':'t_optics', 'parents':[]}
    requires = None

@register_upgrade
class Optics2aUpgrade(Upgrade):
    name = "t_optics2a"
    resource_type = "gas"
    category = "tech"
    title = "Interference Plating"
    description = "[Battleships] gain [^+67%] Maximum Health, other ships have [!-33%] Maximum Health"
    icon = "interferenceplating"
    stats = Stats(ship_health_mul=-0.33, battleship_health_mul=1)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics2bUpgrade(Upgrade):
    name = "t_optics2b"
    resource_type = "gas"
    category = "tech"
    title = "Auto Focus"
    description = "Ships gradually gain Attack Speed while flying, up to [^+50%] over 60 seconds"
    icon = "autofocus"
    stats = Stats(fire_rate_over_time=0.5)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics3Upgrade(Upgrade):
    name = "t_optics3"
    resource_type = "gas"
    category = "tech"
    title = "Fleet Refractor"
    description = "Ships in a fleet of [4 or more] gain [^+10] Shield"
    icon = "fleetrefractor"
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
    title = "Supercollector"
    description = "Gain [^+200%] Resources from asteroids"
    icon = "supercollector"
    stats = Stats(asteroid_yield_mul=2.0)
    family = {'tree':'t_exotic', 'parents':[]}
    requires = None


@register_upgrade
class Exotic2aUpgrade(Upgrade):
    name = "t_exotic2a"
    resource_type = "gas"
    category = "tech"
    title = "Projectile Accelerator"
    description = "Ships gain [^+35%] Attack Range"
    icon = "projectileaccelerator"
    stats = Stats(ship_weapon_range=0.35)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

# TODO: replace
@register_upgrade
class Exotic2bUpgrade(Upgrade):
    name = "t_exotic2b"
    resource_type = "gas"
    category = "tech"
    title = "Jettison"
    description = "When a planet you control is razed, gain [^2 full upgrades] of the its Primary Resource"
    icon = "jettison"
    stats = Stats(lost_planet_upgrade=2)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

@register_upgrade
class Exotic3Upgrade(Upgrade):
    name = "t_exotic3"
    resource_type = "gas"
    category = "tech"
    title = "Mine Pack"
    description = "Your next 10 ships that die drop a Mine upon death"
    icon = "minepack"
    stats = Stats()
    family = {'tree':'t_exotic', 'parents':['t_exotic2a', 't_exotic2b']}
    requires = lambda x: 't_exotic1' in x and ('t_exotic2a' in x or 't_exotic2b' in x)
    infinite = True

    def apply(self, to):
        to.ships_dropping_mines += 10
        return super().apply(to)

### 10) Alien - yellow
@register_upgrade
class Alien1Upgrade(Upgrade):
    name = "t_alien1"
    resource_type = "gas"
    category = "tech"
    title = "Void Cover"
    description = "[Scouts] gain Cloaking"
    icon = "voidcover"
    stats = Stats(scout_stealth=1)
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
    title = "Curious Artifact"
    description = "Gain [^+3] Rerolls"
    icon = "curiousartifact"
    stats = Stats()
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)

    def apply(self, to):
        game.Game.inst.run_info.rerolls += 3
        return super().apply(to)    

@register_upgrade
class Alien2bUpgrade(Upgrade):
    name = "t_alien2b"
    resource_type = "gas"
    category = "tech"
    title = "Kinetic Sling"
    description = "Each ship's weapon deals [^up to +4] Damage based on its bonus speed"
    icon = "kineticsling"
    stats = Stats(ship_weapon_damage_speed=4)
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)
    infinite = True

@register_upgrade
class Alien3Upgrade(Upgrade):
    name = "t_alien3"
    resource_type = "gas"
    category = "tech"
    title = "Atmosphere Capture"
    description = "Gain [+30] Oxygen per planet you control"
    icon = "atmospherecapture"
    stats = Stats()
    family = {'tree':'t_alien', 'parents':['t_alien2a', 't_alien2b']}
    requires = lambda x: 't_alien1' in x and ('t_alien2a' in x or 't_alien2b' in x)

    def apply(self, to):
        # TODO: Effect
        for planet in to.scene.get_civ_planets(to):
            to.scene.game.run_info.o2 += 30
        return super().apply(to)
    


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
