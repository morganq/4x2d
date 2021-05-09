from upgrade.upgrades import register_upgrade, Upgrade
from stats import Stats
import random

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
    title = "Decommission"
    description = "3 random [Fighters] you control are [!destroyed]. Gain [^4] population among 4 random planets."
    icon = "decommission"
    stats = Stats()
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

    def apply(self, to):
        all_fighters = to.get_all_fighters()
        random.shuffle(all_fighters)
        for f in all_fighters[:3]:
            if f['type'] == 'ship':
                f['object'].kill()
            elif f['type'] == 'planet':
                f['object'].ships['fighter'] -= 1
                f['object'].needs_panel_update = True

        my_planets = to.scene.get_civ_planets(to)
        for i in range(4):
            random.choice(my_planets).population += 1

        return super().apply(to)

@register_upgrade
class Mechanics2bUpgrade(Upgrade):
    name = "t_mechanics2b"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Boosters"
    description = "Ships fly [^+33%] faster when targeting enemy planets"
    icon = "vanguardboosters"
    stats = Stats(ship_speed_mul_targeting_planets = 0.33)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

@register_upgrade
class Mechanics3Upgrade(Upgrade):
    name = "t_mechanics3"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Armor"
    description = "Ships gain a [^+10] health shield when far from a planet you control"
    icon = "vanguardarmor"
    stats = Stats(ship_shield_far_from_home = 100)
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
    description = "[^+10%] mining rate. A random fighter you control is [!destroyed] every minute"
    icon = "nuclearbattery"
    stats = Stats(mining_rate=0.1, nuclear_instability=1)
    family = {'tree':'t_atomic', 'parents':[]}
    requires = None

@register_upgrade
class Atomic2aUpgrade(Upgrade):
    name = "t_atomic2a"
    resource_type = "iron"
    category = "tech"
    title = "Isotope Conversion"
    description = "Gain [100] ice and [50] gas. <iron> is [!frozen] for 20 seconds."
    icon = "isotope"
    stats = Stats()
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)

    def apply(self, to):
        to.resources.ice += 100
        to.resources.gas += 50
        to.frozen.iron += 20
        return super().apply(to)

@register_upgrade
class Atomic2bUpgrade(Upgrade):
    name = "t_atomic2b"
    resource_type = "iron"
    category = "tech"
    title = "Atomic Assembler"
    description = "[^+15%] faster production of ships other than [Fighters]"
    icon = "atomicassembler"
    stats = Stats(bomber_production=0.15, interceptor_production=0.15, battleship_production=0.15)
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)

@register_upgrade
class Atomic3Upgrade(Upgrade):
    name = "t_atomic3"
    resource_type = "iron"
    category = "tech"
    title = "Unstable Reactor"
    description = "Mining rate on each planet slowly grows to [^+10%], but [!resets] if attacked or if a ship is launched"
    icon = "unstablereactor"
    stats = Stats(unstable_reaction = 0.10)
    family = {'tree':'t_atomic', 'parents':['t_atomic2a', 't_atomic2b']}
    requires = lambda x: 't_atomic1' in x and ('t_atomic2a' in x or 't_atomic2b' in x)
    infinite = True

### 3) Biologic: skin color
@register_upgrade
class Bio1Upgrade(Upgrade):
    name = "t_bio1"
    resource_type = "iron"
    category = "tech"
    title = "Symbiosis"
    description = "Planets gain [^+10] health per construction"
    icon = "preciseassembly"
    stats = Stats(planet_health_per_construct=10)
    family = {'tree':'t_bio', 'parents':[]}
    requires = None

@register_upgrade
class Bio2aUpgrade(Upgrade):
    name = "t_bio2a"
    resource_type = "iron"
    category = "tech"
    title = "Overgrowth"
    description = "Population grows [^+5%] faster for each docked ship"
    icon = "decommission"
    stats = Stats(pop_growth_rate_per_docked_ship = 5)
    family = {'tree':'t_bio', 'parents':['t_bio1']}
    requires = ('t_bio1',)

@register_upgrade
class Bio2bUpgrade(Upgrade):
    name = "t_bio2b"
    resource_type = "iron"
    category = "tech"
    title = "Metabolic Cycle"
    description = "Planets gain [^+2] health per second if no ships are docked"
    icon = "vanguardboosters"
    stats = Stats(planet_regen_without_ships = 2)
    family = {'tree':'t_bio', 'parents':['t_bio1']}
    requires = ('t_bio1',)

@register_upgrade
class Bio3Upgrade(Upgrade):
    name = "t_bio3"
    resource_type = "iron"
    category = "tech"
    title = "Root"
    description = "Enemy ships near your planets move and attack 25% slower"
    icon = "vanguardarmor"
    stats = Stats(planet_slow_aura=0.25)
    family = {'tree':'t_bio', 'parents':['t_bio2a', 't_bio2b']}
    requires = lambda x: 't_bio1' in x and ('t_bio2a' in x or 't_bio2b' in x)
    infinite = False


### 4) Quantum: grey purple
@register_upgrade
class Quantum1Upgrade(Upgrade):
    name = "t_quantum1"
    resource_type = "iron"
    category = "tech"
    title = "Material Reconstruction"
    description = "Gain [^+25] ice for each planet you control"
    icon = "preciseassembly"
    stats = Stats()
    family = {'tree':'t_quantum', 'parents':[]}
    requires = None

    def apply(self, to):
        pass #impl
        return super().apply(to)

@register_upgrade
class Quantum2aUpgrade(Upgrade):
    name = "t_quantum2a"
    resource_type = "iron"
    category = "tech"
    title = "Nanothread Plating"
    description = "Ships have [^+25%] health"
    icon = "decommission"
    stats = Stats(ship_health_mul = 0.25)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)

@register_upgrade
class Quantum2bUpgrade(Upgrade):
    name = "t_quantum2b"
    resource_type = "iron"
    category = "tech"
    title = "Warp Drive"
    description = "Ships gain warp drive, and can teleport forward [^+5] units in open space"
    icon = "vanguardboosters"
    stats = Stats(warp_drive = 5)
    family = {'tree':'t_quantum', 'parents':['t_quantum1']}
    requires = ('t_quantum1',)
    infinite = True

@register_upgrade
class Quantum3Upgrade(Upgrade):
    name = "t_quantum3"
    resource_type = "iron"
    category = "tech"
    title = "Quantum Weirdness"
    description = "A colonist ship that uses warp drive has a [50% chance] for [^+1] population"
    icon = "vanguardarmor"
    stats = Stats(planet_slow_aura=0.10)
    family = {'tree':'t_quantum', 'parents':['t_quantum2b']}
    requires = ('t_quantum2b',)
    infinite = False

### 5) Crystal - Interceptor / contain: blue
@register_upgrade
class Crystal1Upgrade(Upgrade):
    name = "t_crystal1"
    resource_type = "ice"
    category = "tech"
    title = "Resonance Reloader"
    description = "[Interceptors] fire [^+33%] faster in deep space"
    icon = "resonancereloader"
    stats = Stats(interceptor_fire_rate_deep_space=0.33)
    family = {'tree':'t_crystal', 'parents':[]}
    requires = None

@register_upgrade
class Crystal2aUpgrade(Upgrade):
    name = "t_crystal2a"
    resource_type = "ice"
    category = "tech"
    title = "Phasing Lattice"
    description = "Ships near enemy planets have a [+15%] chance to dodge missile weapons"
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
    description = "Interceptor missiles bounce to [^+1] nearby target"
    icon = "crystalrepeater"
    stats = Stats(interceptor_missile_bounce=1)
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
    description = "Ships gain [^+100%] attack speed for 4 seconds after take-off"
    icon = "resonancereloader"
    stats = Stats(ship_fire_rate_after_takeoff=100)
    family = {'tree':'t_ai', 'parents':[]}
    requires = None

@register_upgrade
class AI2aUpgrade(Upgrade):
    name = "t_ai2a"
    resource_type = "ice"
    category = "tech"
    title = "Artificial Intelligence"
    description = "Population grows on planets even with 0 population"
    icon = "phasinglattice"
    stats = Stats(pop_growth_min_reduction=1)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)

@register_upgrade
class AI2bUpgrade(Upgrade):
    name = "t_ai2b"
    resource_type = "ice"
    category = "tech"
    title = "Robotic Assembly"
    description = "Whenever you gain control of a planet, add a random tier 1 building"
    icon = "fragmentationsequence"
    stats = Stats(colonize_random_building=1)
    family = {'tree':'t_ai', 'parents':['t_ai1']}
    requires = ('t_ai1',)

@register_upgrade
class AI3Upgrade(Upgrade):
    name = "t_ai3"
    resource_type = "ice"
    category = "tech"
    title = "Coordination Protocol"
    description = "Interceptors fire [^+20%] faster near bombers"
    icon = "tech_default"
    stats = Stats(interceptor_fire_rate_near_bombers=0.20)
    family = {'tree':'t_ai', 'parents':['t_ai2a', 't_ai2b']}
    requires = lambda x: 't_ai1' in x and ('t_ai2a' in x or 't_ai2b' in x)
    infinite = True

### 7) Proximity - Dark grey
@register_upgrade
class Proximity1Upgrade(Upgrade):
    name = "t_proximity1"
    resource_type = "ice"
    category = "tech"
    title = "Fire Bomb"
    description = "Bombers have a 10% chance to destroy a random building on hit"
    icon = "resonancereloader"
    stats = Stats(bomber_raze_chance=0.1)
    family = {'tree':'t_proximity', 'parents':[]}
    requires = None

@register_upgrade
class Proximity2aUpgrade(Upgrade):
    name = "t_proximity2a"
    resource_type = "ice"
    category = "tech"
    title = "Proximity Alert"
    description = "Planets you control that are near enemy planets produce ships [^+15%] faster"
    icon = "phasinglattice"
    stats = Stats(ship_production_proximity=0.15)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity2bUpgrade(Upgrade):
    name = "t_proximity2b"
    resource_type = "ice"
    category = "tech"
    title = "Unnamed"
    description = "Planets you control that are near hazards gain [^+15%] mining rate"
    icon = "fragmentationsequence"
    stats = Stats(mining_rate_proximity=0.15)
    family = {'tree':'t_proximity', 'parents':['t_proximity1']}
    requires = ('t_proximity1',)

@register_upgrade
class Proximity3Upgrade(Upgrade):
    name = "t_proximity3"
    resource_type = "ice"
    category = "tech"
    title = "proximity Repeater"
    description = "Bomber damage [^+25%]"
    icon = "mining"
    stats = Stats(bomber_damage_mul=0.25)
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
    description = "Battleships rapidly fire lasers instead of missiles"
    icon = "resonancereloader"
    stats = Stats(battleship_laser=1)
    family = {'tree':'t_optics', 'parents':[]}
    requires = None

@register_upgrade
class Optics2aUpgrade(Upgrade):
    name = "t_optics2a"
    resource_type = "gas"
    category = "tech"
    title = "Fleet Upgrade"
    description = "Battleships gain [^+50%] health, other ships have [!-25%] health"
    icon = "phasinglattice"
    stats = Stats(ship_health_mul=-0.25, battleship_health_mul=0.75)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics2bUpgrade(Upgrade):
    name = "t_optics2b"
    resource_type = "ice"
    category = "tech"
    title = "Auto Focus"
    description = "Ships gradually gain attack speed while flying, up to [^+35%] over [60 seconds]"
    icon = "fragmentationsequence"
    stats = Stats(fire_rate_over_time=0.35)
    family = {'tree':'t_optics', 'parents':['t_optics1']}
    requires = ('t_optics1',)

@register_upgrade
class Optics3Upgrade(Upgrade):
    name = "t_optics3"
    resource_type = "ice"
    category = "tech"
    title = "EM Enclosure"
    description = "A group of 8 or more ships gains a [^20] damage shield"
    icon = "mining"
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
    description = "Gain [^+50%] resources from asteroids"
    icon = "tech_default"
    stats = Stats(asteroid_yield_mul=0.5)
    family = {'tree':'t_exotic', 'parents':[]}
    requires = None

@register_upgrade
class Exotic2aUpgrade(Upgrade):
    name = "t_exotic2a"
    resource_type = "gas"
    category = "tech"
    title = "Transient Field"
    description = "Planets gain [^+100%] health for the first minute you control them"
    icon = "tech_default"
    stats = Stats(planet_temp_health_mul=1.0)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

@register_upgrade
class Exotic2bUpgrade(Upgrade):
    name = "t_exotic2b"
    resource_type = "gas"
    category = "tech"
    title = "Gravitational Reinforcement"
    description = "Planets gain [^+50%] health if near other planets you control"
    icon = "tech_default"
    stats = Stats(planet_proximity_health_mul=0.5)
    family = {'tree':'t_exotic', 'parents':['t_exotic1']}
    requires = ('t_exotic1',)

@register_upgrade
class Exotic3Upgrade(Upgrade):
    name = "t_exotic3"
    resource_type = "gas"
    category = "tech"
    title = "Relativistic Targeting"
    description = "Ships gain [^+15%] attack range"
    icon = "tech_default"
    stats = Stats(ship_weapon_range=0.15)
    family = {'tree':'t_exotic', 'parents':['t_exotic2a', 't_exotic2b']}
    requires = lambda x: 't_exotic1' in x and ('t_exotic2a' in x or 't_exotic2b' in x)
    infinite = True

### 10) Alien - yellow
@register_upgrade
class Alien1Upgrade(Upgrade):
    name = "t_alien1"
    resource_type = "gas"
    category = "tech"
    title = "Unknown Artifact"
    description = "Gain [^3] re-rolls"
    icon = "tech_default"
    stats = Stats()
    family = {'tree':'t_alien', 'parents':[]}
    requires = None

    def apply(self, to):
        # impl
        return super().apply(to)

@register_upgrade
class Alien2aUpgrade(Upgrade):
    name = "t_alien2a"
    resource_type = "gas"
    category = "tech"
    title = "Alien Thrusters"
    description = "Ships move [^+15%] faster"
    icon = "tech_default"
    stats = Stats(ship_speed_mul=0.15)
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)

@register_upgrade
class Alien2bUpgrade(Upgrade):
    name = "t_alien2b"
    resource_type = "gas"
    category = "tech"
    title = "Kinetic Sling"
    description = "Ships deal bonus damage based on bonus speed"
    icon = "tech_default"
    stats = Stats(damage_based_on_speed_bonus=0.5)
    family = {'tree':'t_alien', 'parents':['t_alien1']}
    requires = ('t_alien1',)

@register_upgrade
class Alien3Upgrade(Upgrade):
    name = "t_alien3"
    resource_type = "gas"
    category = "tech"
    title = "Alien Core Drill"
    description = "Ice production is [^+10%] faster, gas production is [^+5%] faster"
    icon = "tech_default"
    stats = Stats(ice_mining_rate=0.1, gas_mining_rate=0.05)
    family = {'tree':'t_alien', 'parents':['t_alien2a', 't_alien2b']}
    requires = lambda x: 't_alien1' in x and ('t_alien2a' in x or 't_alien2b' in x)
    infinite = True