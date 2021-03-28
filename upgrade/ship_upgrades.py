from upgrade.upgrades import register_upgrade, Upgrade
from productionorder import ProductionOrder

@register_upgrade
class Basic1Upgrade(Upgrade):
    name = "basicfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "[^4] [Fighters] Over 30 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 30)
        to.add_production(p)

@register_upgrade
class Basic2Upgrade(Upgrade):
    name = "basicfighters2"
    resource_type = "iron"
    category = "ships"
    title = "Expedited Order"
    description = "[^4] [Fighters] Over 25 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':['basicfighters1']}
    requires = ('basicfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 25)
        to.add_production(p)  

@register_upgrade
class Basic3Upgrade(Upgrade):
    name = "basicfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Rush Order"
    description = "[^4] [Fighters] Over 20 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':['basicfighters2']}
    requires = ('basicfighters1', 'basicfighters2')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 20)
        to.add_production(p)                

@register_upgrade
class InstantFighters1Upgrade(Upgrade):
    name = "instantfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Emergency Reinforcements"
    description = "[^2] [Fighters] [^Instantly]"
    icon = "fighters30"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 0.25)
        to.add_production(p)

@register_upgrade
class InstantFighters2aUpgrade(Upgrade):
    name = "instantfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Guard Deployment"
    description = "[^3] [Fighters] [^Instantly], [!-2] [Population]"
    icon = "fighters30"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['instantfighters1']}
    requires = ('instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.population -= 2

@register_upgrade
class InstantFighters2bUpgrade(Upgrade):
    name = "instantfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "War Manufacturing"
    description = "[^3] [Fighters] [^Instantly], Planet loses [!25] [Health]"
    icon = "fighters30"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['instantfighters1']}
    requires = ('instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.health -= 25

@register_upgrade
class InstantFighters3aUpgrade(Upgrade):
    name = "instantfighters3a"
    resource_type = "iron"
    category = "ships"
    title = "Guard Deployment II"
    description = "[^4] [Fighters] [^Instantly], [!-3] [Population]"
    icon = "fighters30"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['instantfighters2a']}
    requires = ('instantfighters1','instantfighters2a')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 0.25)
        to.add_production(p)        
        to.population -= 3    

@register_upgrade
class InstantFighters3bUpgrade(Upgrade):
    name = "instantfighters3b"
    resource_type = "iron"
    category = "ships"
    title = "War Manufacturing II"
    description = "[^4] [Fighters] [^Instantly], Planet loses [!35] [Health]"
    icon = "fighters30"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['instantfighters2b']}
    requires = ('instantfighters1','instantfighters2b')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 0.25)
        to.add_production(p)        
        to.health -= 35

@register_upgrade
class LongFighters1Upgrade(Upgrade):
    name = "longfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly"
    description = "[^4] [Fighters] Over 90 seconds, [^+50] [Iron]"
    icon = "fighters3pop"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 90)
        to.add_production(p)        
        to.owning_civ.resources.iron += 50

@register_upgrade
class LongFighters2aUpgrade(Upgrade):
    name = "longfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Strategic Assembly"
    description = "[^5] [Fighters] Over 100 seconds"
    icon = "fighters3pop"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['longfighters1']}
    requires = ('longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 5, 100)
        to.add_production(p)

@register_upgrade
class LongFighters2bUpgrade(Upgrade):
    name = "longfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly II"
    description = "[^4] [Fighters] Over 100 seconds, [^+100] [Iron]"
    icon = "fighters3pop"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['longfighters1']}
    requires = ('longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 100)
        to.add_production(p)        
        to.owning_civ.resources.iron += 100

@register_upgrade
class LongFighters3Upgrade(Upgrade):
    name = "longfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Recycled Armaments"
    description = "[^6] [Fighters] Over 120 seconds, [^+50] [Gas]"
    icon = "fighters3pop"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['longfighters2a', 'longfighters2b']}
    requires = lambda x:'longfighters1' in x and ('longfighters2a' in x or 'longfighters2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 6, 120)
        to.add_production(p)        
        to.owning_civ.resources.gas += 50

@register_upgrade
class InterceptorFighters1Upgrade(Upgrade):
    name = "interceptorfighters1"
    resource_type = "ice"
    category = "ships"
    title = "Interceptor Convoy"
    description = "[^2] [Fighters] and [^1] [Interceptor] Over 30 seconds. If Interceptor is not unlocked, [^+1] Population"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'interceptorfighters', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 30)
        to.add_production(p)
        if 'hangar2a' in to.owning_civ.researched_upgrade_names:
            p = ProductionOrder("interceptor", 1, 30)
            to.add_production(p)
        else:
            to.population += 1

@register_upgrade
class Interceptors1Upgrade(Upgrade):
    name = "basicinterceptors1"
    resource_type = "ice"
    category = "ships"
    title = "Interceptors"
    description = "[^2] [Interceptors] Over 30 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':[]}
    requires = ('hangar2a',)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("interceptor", 2, 30)
        to.add_production(p)

@register_upgrade
class Bombers1Upgrade(Upgrade):
    name = "basicbombers1"
    resource_type = "ice"
    category = "ships"
    title = "Bombers"
    description = "[^2] [Bombers] Over 30 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':[]}
    requires = ('hangar2b',)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("bomber", 2, 30)
        to.add_production(p)       

@register_upgrade
class BattleshipFighters1Upgrade(Upgrade):
    name = "battleshipfighters1"
    resource_type = "gas"
    category = "ships"
    title = "Battleship Convoy"
    description = "[^3] [Fighters] and [^1] [Battleship] Over 50 seconds. If Battleship is not unlocked, [^+2] Population"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'battleshipfighters', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 50)
        to.add_production(p)
        if 'hangar3' in to.owning_civ.researched_upgrade_names:
            p = ProductionOrder("battleship", 1, 50)
            to.add_production(p)
        else:
            to.population += 2

@register_upgrade
class Battleships1Upgrade(Upgrade):
    name = "basicbattleships1"
    resource_type = "gas"
    category = "ships"
    title = "Battleships"
    description = "[^2] [Battleships] Over 30 seconds"
    icon = "fighters6"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':[]}
    requires = ('hangar3',)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("battleship", 2, 30)
        to.add_production(p)         