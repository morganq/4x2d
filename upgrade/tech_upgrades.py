from upgrade.upgrades import register_upgrade, Upgrade
from stats import Stats

### 1) Mechanics: Rush ###
@register_upgrade
class Mechanics1Upgrade(Upgrade):
    name = "t_mechanics1"
    resource_type = "iron"
    category = "tech"
    title = "Precise Assembly"
    description = "[Fighters] gain [^+33%] rate of fire"
    icon = "tech_default"
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
    icon = "tech_default"
    stats = None
    family = {'tree':'t_mechanics', 'parents':['t_mechanics1']}
    requires = ('t_mechanics1',)

    def apply(self, to):
        # TODO: implement
        return super().apply(to)

@register_upgrade
class Mechanics2bUpgrade(Upgrade):
    name = "t_mechanics2b"
    resource_type = "iron"
    category = "tech"
    title = "Vanguard Boosters"
    description = "Ships fly [^+33%] faster when targeting enemy planets"
    icon = "tech_default"
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
    icon = "tech_default"
    stats = Stats(ship_armor_far_from_home = 10)
    family = {'tree':'t_mechanics', 'parents':['t_mechanics2a', 't_mechanics2b']}
    requires = lambda x: 't_mechanics1' in x and ('t_mechanics2a' in x or 't_mechanics2b' in x)
    infinite = True

### 2) Atomic - Macro/Quick Tech
@register_upgrade
class Atomic1Upgrade(Upgrade):
    name = "t_atomic1"
    resource_type = "iron"
    category = "tech"
    title = "Nuclear Battery"
    description = "[^+10%] mining rate. A random ship you control is [!destroyed] every minute"
    icon = "tech_default"
    stats = Stats(mining_rate=0.1, nuclear_instability=1)
    family = {'tree':'t_atomic', 'parents':[]}
    requires = None

@register_upgrade
class Atomic2aUpgrade(Upgrade):
    name = "t_atomic2a"
    resource_type = "iron"
    category = "tech"
    title = "Isotope Conversion"
    description = "Gain [100] <ice> and [50] <gas>. <iron> is [!frozen] for 20 seconds."
    icon = "tech_default"
    stats = None
    family = {'tree':'t_atomic', 'parents':['t_atomic1']}
    requires = ('t_atomic1',)

    def apply(self, to):
        # TODO: implement
        return super().apply(to)

@register_upgrade
class Atomic2bUpgrade(Upgrade):
    name = "t_atomic2b"
    resource_type = "iron"
    category = "tech"
    title = "Atomic Assembler"
    description = "[^+15%] faster production of ships other than [Fighters]"
    icon = "tech_default"
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
    icon = "tech_default"
    stats = Stats(unstable_reaction = 0.10)
    family = {'tree':'t_atomic', 'parents':['t_atomic2a', 't_atomic2b']}
    requires = lambda x: 't_atomic1' in x and ('t_atomic2a' in x or 't_atomic2b' in x)
    infinite = True

### 5) Crystal - Interceptor / contain
@register_upgrade
class Crystal1Upgrade(Upgrade):
    name = "t_crystal1"
    resource_type = "ice"
    category = "tech"
    title = "Resonance Reloader"
    description = "[Interceptors] fire [^+33%] faster in deep space"
    icon = "tech_default"
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
    icon = "tech_default"
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
    icon = "tech_default"
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
    icon = "tech_default"
    stats = Stats(interceptor_missile_bounce=1)
    family = {'tree':'t_crystal', 'parents':['t_crystal2a', 't_crystal2b']}
    requires = lambda x: 't_crystal1' in x and ('t_crystal2a' in x or 't_crystal2b' in x)
    infinite = True

### 9) Exotic - variety
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
    resource_type = "iron"
    category = "tech"
    title = "Relativistic Targeting"
    description = "Ships gain [^+15%] attack range"
    icon = "tech_default"
    stats = Stats(ship_weapon_range=0.15)
    family = {'tree':'t_exotic', 'parents':['t_exotic2a', 't_exotic2b']}
    requires = lambda x: 't_exotic1' in x and ('t_exotic2a' in x or 't_exotic2b' in x)
    infinite = True


###########
### OLD ###
###########

class Nanotech1Upgrade(Upgrade):
    name = "nanotech1"
    resource_type = "iron"
    category = "tech"
    title = "Repair Bots"
    description = "[All Ships] regenerate [^+1] [Health/Sec]"
    icon = "tech_default"
    stats = Stats(ship_regenerate=1)
    family = {'tree':'nanotech', 'parents':[]}
    requires = None

class Nanotech2aUpgrade(Upgrade):
    name = "nanotech2a"
    resource_type = "iron"
    category = "tech"
    title = "Hull Reconfiguration"
    description = "When a [Ship] dies, it heals a random nearby [Ally] for [^10] [Health]"
    icon = "tech_default"
    stats = Stats(ship_death_heal=10)
    family = {'tree':'nanotech', 'parents':['nanotech1']}    
    requires = ("nanotech1",)
    infinite = True


class Nanotech2bUpgrade(Upgrade):
    name = "nanotech2b"
    resource_type = "iron"
    category = "tech"
    title = "Grey Goo"
    description = "[!-50%] [Fighter] missile damage. [Fighter] missiles infect the target with [Grey Goo] Nanobots. Each Nanobot deals [0.25] damage per second for each Nanobot"
    icon = "tech_default"
    stats = Stats(grey_goo=1, fighter_damage_mul=-0.5)
    family = {'tree':'nanotech', 'parents':['nanotech1']}    
    requires = ("nanotech1",)


class Nanotech3bUpgrade(Upgrade):
    name = "nanotech3b"
    resource_type = "iron"
    category = "tech"
    title = "Grey Goo"
    description = "Each enemy infected with [Grey Goo] provides [^1] [Iron] per second"
    icon = "tech_default"
    stats = Stats(grey_goo_collection=1)
    family = {'tree':'nanotech', 'parents':['nanotech2b']}    
    requires = ("nanotech1", "nanotech2b")


class Mech1Upgrade(Upgrade):
    name = "mech1"
    resource_type = "iron"
    category = "tech"
    title = "Precise Assembly"
    description = "[All Ships] have [^+15%] rate of fire"
    icon = "tech_default"
    stats = Stats(ship_fire_rate=1)
    family = {'tree':'mech', 'parents':[]}
    requires = None


class Mech2aUpgrade(Upgrade):
    name = "mech2a"
    resource_type = "iron"
    category = "tech"
    title = "Robotics"
    description = "[Population Growth] occurs on planets with [^0] [Population]"
    icon = "tech_default"
    stats = Stats(pop_growth_min_reduction=1)
    family = {'tree':'mech', 'parents':['mech1']}    
    requires = ("mech1",)


class Mech3aUpgrade(Upgrade):
    name = "mech3a"
    resource_type = "iron"
    category = "tech"
    title = "Staged Booster"
    description = "[Ships] have [^+100%] [Max Speed] for [5] seconds after take-off"
    icon = "tech_default"
    stats = Stats(staged_booster_time=5)
    family = {'tree':'mech', 'parents':['mech2a']}    
    requires = ("mech1", "mech2a")


class Mech2bUpgrade(Upgrade):
    name = "mech2b"
    resource_type = "iron"
    category = "tech"
    title = "Shrapnel"
    description = "[Fighter] missiles explode, dealing damage and applying effects in an area."
    icon = "tech_default"
    stats = Stats(fighter_blast_radius=10)
    family = {'tree':'mech', 'parents':['mech1']}
    requires = ("mech1",)



class Mech3bUpgrade(Upgrade):
    name = "mech3b"
    resource_type = "iron"
    category = "tech"
    title = "Accelerated Payload"
    description = "[Ship] weapons deal up to [^+25%] damage based on bonus speed"
    icon = "tech_default"
    stats = Stats(ship_weapon_damage_speed=25)
    family = {'tree':'mech', 'parents':['mech2b']}    
    requires = ("mech1", "mech2b")


class Nuclear1Upgrade(Upgrade):
    name = "nuclear1"
    resource_type = "iron"
    category = "tech"
    title = "Nuclear Battery"
    description = "[All Planets] have [^+15%] mining rate. Every minute, 1 random deployed ship is destroyed"
    icon = "tech_default"
    stats = Stats(mining_rate=0.15, nuclear_instability=1)
    family = {'tree':'nuclear', 'parents':[]}
    requires = None


class Nuclear2aUpgrade(Upgrade):
    name = "nuclear2a"
    resource_type = "iron"
    category = "tech"
    title = "Unstable Reaction"
    description = "[!-10%] mining rate. Each [Planet's] mining rate increases slowly to [^+25%], but resets when the planet is attacked"
    icon = "tech_default"
    stats = Stats(mining_rate = -0.1, unstable_reaction=0.25)
    family = {'tree':'nuclear', 'parents':['nuclear1']}    
    requires = ("nuclear1",)
    infinite = True


class Nuclear2bUpgrade(Upgrade):
    name = "nuclear2b"
    resource_type = "iron"
    category = "tech"
    title = "Atomic Bomb"
    description = "When a worker ship dies, it explodes for [^50] damage. Radius is based on ship population"
    icon = "tech_default"
    stats = Stats(atomic_bomb=1)
    family = {'tree':'nuclear', 'parents':['nuclear1']}    
    requires = ("nuclear1",)


class Nuclear3Upgrade(Upgrade):
    name = "nuclear3b"
    resource_type = "iron"
    category = "tech"
    title = "Quantum Unfolding"
    description = "Unlock [Warp Drive]. [Ships] gain [^+25] [Warp Drive] distance"
    icon = "tech_default"
    stats = Stats(warp_drive=25)
    family = {'tree':'nuclear', 'parents':['nuclear2a', 'nuclear2b']}    
    requires = lambda x:'nuclear1' in x and ('nuclear2a' in x or 'nuclear2b' in x)