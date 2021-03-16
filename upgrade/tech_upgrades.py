from upgrade.upgrades import register_upgrade, Upgrade
from stats import Stats

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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

@register_upgrade
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