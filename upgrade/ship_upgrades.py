import random

import ships
from productionorder import ProductionOrder

from upgrade.upgrades import Upgrade, register_upgrade


@register_upgrade
class Scout1Upgrade(Upgrade):
    name = "s_scouts1"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "Train [^1] [Scout] Over [10 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("scout", 1, 10)
        to.add_production(p)

@register_upgrade
class Scout2aUpgrade(Upgrade):
    name = "s_scouts2a"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "Train [^2] [Scouts] Over [30 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':['s_scouts1']}
    requires = ('s_scouts1',)

    def apply(self, to):
        p = ProductionOrder("scout", 2, 30)
        to.add_production(p)  

@register_upgrade
class Scout2bUpgrade(Upgrade):
    name = "s_scouts2b"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "Train [^2] [Scouts] Over [30 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':['s_scouts1']}
    requires = ('s_scouts1',)

    def apply(self, to):
        p = ProductionOrder("scout", 2, 30)
        to.add_production(p)          

@register_upgrade
class Scout3Upgrade(Upgrade):
    name = "s_scouts3"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "Train [^2] [Scouts] Over [30 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':['s_scouts2a', 's_scouts2b']}
    requires = lambda x:'s_scouts1' in x and ('s_scouts2a' in x or 's_scouts2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("scout", 2, 30)
        to.add_production(p)                

@register_upgrade
class InstantFighters1Upgrade(Upgrade):
    name = "s_instantfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Emergency Reinforcements"
    description = "Train [^1] [Fighter] [^Instantly]"
    icon = "emergencyreinforcements"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 1, 0.25)
        to.add_production(p)

@register_upgrade
class InstantFighters2aUpgrade(Upgrade):
    name = "s_instantfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Guard Deployment"
    description = "Train [^2] [Fighters] [^Instantly], [!-2] population"
    icon = "guarddeployment"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters1']}
    requires = ('s_instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 0.25)
        to.add_production(p)        
        to.population -= 2

@register_upgrade
class InstantFighters2bUpgrade(Upgrade):
    name = "s_instantfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "War Manufacturing"
    description = "Train [^2] [Fighters] [^Instantly], Planet loses [!50] health"
    icon = "warmanufacturing"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters1']}
    requires = ('s_instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 0.25)
        to.add_production(p)        
        to.health -= 50

@register_upgrade
class InstantFighters3aUpgrade(Upgrade):
    name = "s_instantfighters3a"
    resource_type = "iron"
    category = "ships"
    title = "Guard Deployment II"
    description = "Train [^3] [Fighters] [^Instantly], [!-2] population"
    icon = "guarddeployment2"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters2a']}
    requires = ('s_instantfighters1','s_instantfighters2a')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.population -= 2

@register_upgrade
class InstantFighters3bUpgrade(Upgrade):
    name = "s_instantfighters3b"
    resource_type = "iron"
    category = "ships"
    title = "War Manufacturing II"
    description = "Train [^3] [Fighters] [^Instantly], Planet loses [!80] health"
    icon = "warmanufacturing2"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters2b']}
    requires = ('s_instantfighters1','s_instantfighters2b')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.health -= 80

@register_upgrade
class LongFighters1Upgrade(Upgrade):
    name = "s_longfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly"
    description = "Train [^3] [Fighters] Over [120 seconds], [^+50] Iron"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 120)
        to.add_production(p)        
        to.owning_civ.earn_resource("iron", 50)

@register_upgrade
class LongFighters2aUpgrade(Upgrade):
    name = "s_longfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Strategic Assembly"
    description = "Train [^4] [Fighters] Over [120 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 120)
        to.add_production(p)

@register_upgrade
class LongFighters2bUpgrade(Upgrade):
    name = "s_longfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly II"
    description = "Train [^3] [Fighters] Over [120 seconds], [^+100] Iron"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 120)
        to.add_production(p)        
        to.owning_civ.earn_resource("iron", 100)

@register_upgrade
class LongFighters3Upgrade(Upgrade):
    name = "s_longfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly III"
    description = "Train [^4] [Fighters] Over [120 seconds], [^+50] Gas"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters2a', 's_longfighters2b']}
    requires = lambda x:'s_longfighters1' in x and ('s_longfighters2a' in x or 's_longfighters2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 5, 120)
        to.add_production(p)        
        to.owning_civ.resources.gas += 50

@register_upgrade
class Warp1Upgrade(Upgrade):
    name = "s_warp1"
    resource_type = "iron"
    category = "ships"
    title = "Fleet Warp"
    description = "Every ship warps into range of its target and gains [^+67%] attack speed for [6 seconds]"
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':[]}

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.command_warp()

@register_upgrade
class Warp2Upgrade(Upgrade):
    name = "s_warp2"
    resource_type = "iron"
    category = "ships"
    title = "Fleet Warp II"
    description = "Every ship is [^fully repaired], warps into range of its target, and gains [^+67%] attack speed for [6 seconds]"
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':['s_warp1']}
    requires = ('s_warp1',)
    infinite = True

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.health = ship.get_max_health()
            ship.command_warp()            

#### ICE ####

@register_upgrade
class Interceptors1Upgrade(Upgrade):
    name = "s_basicinterceptors1"
    resource_type = "ice"
    category = "ships"
    title = "Interceptor"
    description = "Train [^1] [Interceptor] Over [10 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("interceptor", 1, 10)
        to.add_production(p)

@register_upgrade
class Interceptors2Upgrade(Upgrade):
    name = "s_basicinterceptors2"
    resource_type = "ice"
    category = "ships"
    title = "Interceptor II"
    description = "Train [^2] [Interceptors] Over [45 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':['s_basicinterceptors1']}
    requires = ('s_basicinterceptors1',)

    def apply(self, to):
        p = ProductionOrder("interceptor", 2, 45)
        to.add_production(p)

@register_upgrade
class Interceptors3aUpgrade(Upgrade):
    name = "s_basicinterceptors3a"
    resource_type = "ice"
    category = "ships"
    title = "Interceptor Assembly Line"
    description = "Train [^3] [Interceptors] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':['s_basicinterceptors2']}
    requires = ('s_basicinterceptors1', 's_basicinterceptors2')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("interceptor", 3, 60)
        to.add_production(p)

@register_upgrade
class Interceptors3bUpgrade(Upgrade):
    name = "s_basicinterceptors3b"
    resource_type = "ice"
    category = "ships"
    title = "Ad-Hoc Interceptors"
    description = "Train [^2] [Interceptors] Instantly"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':['s_basicinterceptors2']}
    requires = ('s_basicinterceptors1', 's_basicinterceptors2')

    def apply(self, to):
        p = ProductionOrder("interceptor", 2, 0.5)
        to.add_production(p)        

@register_upgrade
class Bombers1Upgrade(Upgrade):
    name = "s_basicbombers1"
    resource_type = "ice"
    category = "ships"
    title = "Bomb Squadron"
    description = "Train [^2] [Bombers] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':[]}
    

    def apply(self, to):
        p = ProductionOrder("bomber", 2, 60)
        to.add_production(p)  

@register_upgrade
class Bombers2aUpgrade(Upgrade):
    name = "s_basicbombers2a"
    resource_type = "ice"
    category = "ships"
    title = "Bomb Squadron II"
    description = "Train [^3] [Bombers] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':['s_basicbombers1']}
    requires = ('s_basicbombers1',)

    def apply(self, to):
        p = ProductionOrder("bomber", 3, 60)
        to.add_production(p) 

@register_upgrade
class Bombers2bUpgrade(Upgrade):
    name = "s_basicbombers2b"
    resource_type = "ice"
    category = "ships"
    title = "Bomb Support"
    description = "Train [^2] [Bombers] Over [45 seconds], [^+150] [Iron]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':['s_basicbombers1']}
    requires = ('s_basicbombers1',)

    def apply(self, to):
        p = ProductionOrder("bomber", 2, 45)
        to.add_production(p)                
        to.owning_civ.earn_resource("iron", 150)

@register_upgrade
class Bombers3Upgrade(Upgrade):
    name = "s_basicbombers3"
    resource_type = "ice"
    category = "ships"
    title = "Bomb Support II"
    description = "Train [^3] [Bombers] Over [60 seconds], [^+75] [Gas]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':['s_basicbombers2a', 's_basicbombers2b']}
    requires = lambda x: 's_basicbombers1' in x and ('s_basicbombers2a' in x or 's_basicbombers2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("bomber", 3, 60)
        to.add_production(p)
        to.owning_civ.earn_resource("gas", 75)        

@register_upgrade
class HangarProduction1Upgrade(Upgrade):
    name = "s_hangarprod1"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing"
    description = "Train [^1] [Fighter], [^1] [Interceptor], and [^1] [Bomber] over 60 seconds at random planets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':[]}

    def apply(self, to):
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("fighter", 1, 20))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("interceptor", 1, 40))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("bomber", 1, 60))

@register_upgrade
class HangarProduction2Upgrade(Upgrade):
    name = "s_hangarprod2"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing II"
    description = "Train [^1] [Fighter], [^1] [Interceptor], and [^1] [Bomber] instantly at random planets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':['hangarprod1']}
    requires = ('hangarprod1',)
    infinite = True

    def apply(self, to):
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("fighter", 1, 0.2))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("interceptor", 1, 0.4))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("bomber", 1, 0.6))            


### GAS ####

@register_upgrade
class Battleships1Upgrade(Upgrade):
    name = "s_basicbattleships1"
    resource_type = "gas"
    category = "ships"
    title = "Battleship"
    description = "Train [^1] [Battleship] Over [30 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 30)
        to.add_production(p)  

@register_upgrade
class Battleships2Upgrade(Upgrade):
    name = "s_basicbattleships2"
    resource_type = "gas"
    category = "ships"
    title = "Battleship II"
    description = "Train [^1] [Battleship] Over [20 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships1']}
    requires = ('s_basicbattleships1',)

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 20)
        to.add_production(p)

@register_upgrade
class Battleships3aUpgrade(Upgrade):
    name = "s_basicbattleships3a"
    resource_type = "gas"
    category = "ships"
    title = "Emergency Battleship"
    description = "Train [^1] [Battleship] [^instantly]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships2']}
    requires = ('s_basicbattleships1', 's_basicbattleships2')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 0.5)
        to.add_production(p)

@register_upgrade
class Battleships3bUpgrade(Upgrade):
    name = "s_basicbattleships3b"
    resource_type = "gas"
    category = "ships"
    title = "Battleship III"
    description = "Train [^2] [Battleships] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships2']}
    requires = ('s_basicbattleships1', 's_basicbattleships2')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("battleship", 2, 60)
        to.add_production(p)

@register_upgrade
class PerPlanetProduction1Upgrade(Upgrade):
    name = "s_perplanet1"
    resource_type = "gas"
    category = "ships"
    title = "Planetary Guard"
    description = "Train [^1] [Fighter] over [40 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':[]}

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("fighter", 1, 40))

@register_upgrade
class PerPlanetProduction1Upgrade(Upgrade):
    name = "s_perplanet2"
    resource_type = "gas"
    category = "ships"
    title = "Planetary Guard II"
    description = "Train [^1] [Fighter] over [10 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':['s_perplanet1']}
    requires = ('s_perplanet1',)
    infinite = True

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("fighter", 1, 10))            

@register_upgrade
class VarietyProduction1Upgrade(Upgrade):
    name = "s_variety1"
    resource_type = "gas"
    category = "ships"
    title = "Armada"
    description = "Train [^2] [Bombers] and [^2] [Interceptors] over [45 seconds]. [Iron] is [!Frozen] for [20 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'variety', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("bomber", 2, 45)
        to.add_production(p)  
        p = ProductionOrder("interceptor", 2, 45)
        to.add_production(p)          
        to.owning_civ.frozen.iron += 20

@register_upgrade
class VarietyProduction2Upgrade(Upgrade):
    name = "s_variety2"
    resource_type = "gas"
    category = "ships"
    title = "Armada II"
    description = "Train [^2] [Bombers], [^2] [Interceptors], and [^2] [Fighters] over [45 seconds]. [Iron] is [!Frozen] for [20 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'variety', 'parents':['s_variety1']}
    requires = ('s_variety1')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 45)
        to.add_production(p)
        p = ProductionOrder("bomber", 2, 45)
        to.add_production(p)
        p = ProductionOrder("interceptor", 2, 45)
        to.add_production(p)
        to.owning_civ.frozen.iron += 20



##########
# UNUSED #
##########

class Heal1Upgrade(Upgrade):
    name = "s_heal1"
    resource_type = "iron"
    category = "ships"
    title = "Fleet Heal"
    description = "Every ship instantly recovers [^10] health"
    icon = "ship_default"
    cursor = None
    family = {'tree':'heal', 'parents':[]}

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.health += 10

class InterceptorFighters1Upgrade(Upgrade):
    name = "s_interceptorfighters1"
    resource_type = "ice"
    category = "ships"
    title = "Interceptor Convoy"
    description = "Train [^1] [Fighter] and [^1] [Interceptor] Over [30 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'interceptorfighters', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 1, 30)
        to.add_production(p)
        p = ProductionOrder("interceptor", 1, 30)
        to.add_production(p)            
