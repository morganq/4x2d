import random

import ships
from productionorder import ProductionOrder

from upgrade.upgrades import Upgrade, register_upgrade


@register_upgrade
class InstantFighters1Upgrade(Upgrade):
    name = "s_instantfighters1"
    resource_type = "iron"
    category = "ships"
    title = "?"
    description = "Train [^1] [Fighter] Over 20 seconds"
    icon = "emergencyreinforcements"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 1, 20)
        to.add_production(p)

@register_upgrade
class InstantFighters2aUpgrade(Upgrade):
    name = "s_instantfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "?"
    description = "Train [^2] [Fighters] over 20 seconds"
    icon = "guarddeployment"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters1']}
    requires = ('s_instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 20)
        to.add_production(p)        

@register_upgrade
class InstantFighters2bUpgrade(Upgrade):
    name = "s_instantfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "?"
    description = "Train [^2] [Fighters] [^Instantly], Iron is [!Frozen] for 15 seconds."
    icon = "warmanufacturing"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters1']}
    requires = ('s_instantfighters1',)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 0.25)
        to.add_production(p)
        to.owning_civ.frozen.iron += 15

@register_upgrade
class InstantFighters3Upgrade(Upgrade):
    name = "s_instantfighters3"
    resource_type = "iron"
    category = "ships"
    title = "?"
    description = "Train [^4] [Fighters] [^Instantly], [!-2] population"
    icon = "guarddeployment2"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters2a', 's_instantfighters2b']}
    requires = lambda x: 's_instantfighters1' in x and ('s_instantfighters2a' in x or 's_instantfighters2b' in x)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 0.25)
        to.add_production(p)        
        to.population -= 2

@register_upgrade
class LongFighters1Upgrade(Upgrade):
    name = "s_longfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly"
    description = "Train [^2] [Fighters] Over [120 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 120)
        to.add_production(p)

@register_upgrade
class LongFighters2aUpgrade(Upgrade):
    name = "s_longfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Strategic Assembly"
    description = "Train [^3] [Fighters] Over [120 seconds]. [^+100] Ice"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 120)
        to.add_production(p)
        to.owning_civ.earn_resource("ice", 100)

@register_upgrade
class LongFighters2bUpgrade(Upgrade):
    name = "s_longfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly II"
    description = "Train [^4] [Fighters] Over [200 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 200)
        to.add_production(p)        

@register_upgrade
class LongFighters3Upgrade(Upgrade):
    name = "s_longfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly III"
    description = "Train [^4] [Fighters] Over [200 seconds], [^+50] Gas"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters2a', 's_longfighters2b']}
    requires = lambda x:'s_longfighters1' in x and ('s_longfighters2a' in x or 's_longfighters2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 200)
        to.add_production(p)        
        to.owning_civ.resources.gas += 50

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
    description = "Train [^1] [Scout] over 60 seconds for every 2 population"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':['s_scouts1']}
    requires = ('s_scouts1',)

    def apply(self, to):
        p = ProductionOrder("scout", to.population // 2, 60)
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
    description = "Train [^2] [Scouts] Over [10 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'scouts', 'parents':['s_scouts2a', 's_scouts2b']}
    requires = lambda x:'s_scouts1' in x and ('s_scouts2a' in x or 's_scouts2b' in x)
    infinite = True

    def apply(self, to):
        p = ProductionOrder("scout", 2, 10)
        to.add_production(p)                


@register_upgrade
class Warp1Upgrade(Upgrade):
    name = "s_warp1"
    resource_type = "iron"
    category = "ships"
    title = "Fleet Warp"
    description = "Every ship warps into range of its target and gains [^+33%] attack speed for [6 seconds]"
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':[]}

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.command_warp()

@register_upgrade
class Warp2aUpgrade(Upgrade):
    name = "s_warp2a"
    resource_type = "iron"
    category = "ships"
    title = "Fleet Warp II"
    description = "Every ship is [^fully repaired], warps into range of its target, and gains [^+33%] attack speed for [6 seconds]"
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':['s_warp1']}
    requires = ('s_warp1',)

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.health = ship.get_max_health()
            ship.command_warp()           

@register_upgrade
class Warp2bUpgrade(Upgrade):
    name = "s_warp2b"
    resource_type = "iron"
    category = "ships"
    title = "Strange Warp"
    description = "Every in-flight ship warps into range of its target, and gains [^+33%] attack speed for [6 seconds]. Add a 3-population worker ship to a random fleet."
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':['s_warp1']}
    requires = ('s_warp1',)

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.command_warp()        
        fm = to.scene.get_fleet_manager(to)
        fleet = random.choice(fm.current_fleets)
        fleet.update_size_info()
        s = ships.colonist.Colonist(to.scene, fleet.pos, to)
        s.set_pop(3)
        s.set_target(fleet.target)
        to.scene.game_group.add(s)        

@register_upgrade
class Warp3Upgrade(Upgrade):
    name = "s_warp3"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "All in-flight non-fighter ships gain a [^15 damage] [Shield]"
    icon = "standardorder"
    cursor = None
    family = {'tree':'warp', 'parents':['s_warp2a', 's_warp2b']}
    requires = lambda x:'s_warp1' in x and ('s_warp2a' in x or 's_warp2b' in x)
    infinite = True

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            if ship.SHIP_BONUS_NAME != "fighter":
                ship.add_shield(15)

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
    title = "?"
    description = "Train [^3] [Interceptors] at random planets Over [20 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':['s_basicinterceptors2']}
    requires = ('s_basicinterceptors1', 's_basicinterceptors2')
    infinite = True

    def apply(self, to):
        for i in range(3):
            p = random.choice(to.scene.get_civ_planets(to))
            p.add_production(ProductionOrder("interceptor", 1, 7 * (i+1)))  

@register_upgrade
class Interceptors3bUpgrade(Upgrade):
    name = "s_basicinterceptors3b"
    resource_type = "ice"
    category = "ships"
    title = "?"
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
    description = "Train [^1] [Interceptor] and [^1] [Bomber] over 60 seconds at random planets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':[]}

    def apply(self, to):
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("interceptor", 1, 30))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("bomber", 1, 60))

@register_upgrade
class HangarProduction2aUpgrade(Upgrade):
    name = "s_hangarprod2a"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing II"
    description = "Train [^1] [Fighter], [^1] [Interceptor], and [^1] [Bomber] instantly at random planets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':['s_hangarprod1']}
    requires = ('s_hangarprod1',)

    def apply(self, to):
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("fighter", 1, 0.2))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("interceptor", 1, 0.4))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("bomber", 1, 0.6))

@register_upgrade
class HangarProduction2bUpgrade(Upgrade):
    name = "s_hangarprod2b"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing II"
    description = "Train [^2] [Fighters], [^1] [Interceptor], and [^1] [Bomber] over 60 seconds at random planets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':['s_hangarprod1']}
    requires = ('s_hangarprod1',)

    def apply(self, to):
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("fighter", 1, 15))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("fighter", 1, 30))        
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("interceptor", 1, 45))
        p = random.choice(to.scene.get_civ_planets(to))
        p.add_production(ProductionOrder("bomber", 1, 60))

@register_upgrade
class HangarProduction3Upgrade(Upgrade):
    name = "s_hangarprod3"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing III"
    description = "Train [^1] [Interceptor] and [^1] [Bomber] instantly at your newest planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':['s_hangarprod2a', 's_hangarprod2b']}
    requires = lambda x: 's_hangarprod1' in x and ('s_hangarprod2a' in x or 's_hangarprod2b' in x)
    infinite = True

    def apply(self, to):
        newest = sorted(to.scene.get_civ_planets(to), key=lambda x:x.owned_time)[0]
        newest.add_production(ProductionOrder('interceptor', 1, 0.25))
        newest.add_production(ProductionOrder('bomber', 1, 0.25))


### GAS ####

@register_upgrade
class Battleships1Upgrade(Upgrade):
    name = "s_basicbattleships1"
    resource_type = "gas"
    category = "ships"
    title = "Battleship"
    description = "Train [^1] [Battleship] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 60)
        to.add_production(p)  

@register_upgrade
class Battleships2aUpgrade(Upgrade):
    name = "s_basicbattleships2a"
    resource_type = "gas"
    category = "ships"
    title = "Battleship II"
    description = "Train [^1] [Battleship] Over [30 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships1']}
    requires = ('s_basicbattleships1',)

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 30)
        to.add_production(p)

@register_upgrade
class Battleships2bUpgrade(Upgrade):
    name = "s_basicbattleships2b"
    resource_type = "gas"
    category = "ships"
    title = "Emergency Battleship"
    description = "Train [^1] [Battleship] [^instantly]. Gas is [!Frozen] for 15 seconds"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships1']}
    requires = ('s_basicbattleships1',)

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 0.25)
        to.add_production(p)
        to.owning_civ.frozen.gas += 15

@register_upgrade
class Battleships3Upgrade(Upgrade):
    name = "s_basicbattleships3"
    resource_type = "gas"
    category = "ships"
    title = "Battleship III"
    description = "Train [^2] [Battleships] Over [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':['s_basicbattleships2a', 's_basicbattleships2b']}
    requires = lambda x: 's_basicbattleships1' in x and ('s_basicbattleships2a' in x or 's_basicbattleships2b' in x)
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
    description = "Train [^1] [Fighter] over [60 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':[]}

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("fighter", 1, 60))

@register_upgrade
class PerPlanetProduction2aUpgrade(Upgrade):
    name = "s_perplanet2a"
    resource_type = "gas"
    category = "ships"
    title = "Scouting Protocol"
    description = "Train [^1] [Scout] over [30 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':['s_perplanet1']}
    requires = ('s_perplanet1',)

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("scout", 1, 30))

@register_upgrade
class PerPlanetProduction2bUpgrade(Upgrade):
    name = "s_perplanet2b"
    resource_type = "gas"
    category = "ships"
    title = "Planetary Guard II"
    description = "Train [^1] [Fighter] over [20 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':['s_perplanet1']}
    requires = ('s_perplanet1',)

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("fighter", 1, 20))

@register_upgrade
class PerPlanetProduction3Upgrade(Upgrade):
    name = "s_perplanet3"
    resource_type = "gas"
    category = "ships"
    title = "Planetary Guard III"
    description = "Train [^1] [Fighter] over [10 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':['s_perplanet2a', 's_perplanet2b']}
    requires = lambda x:'s_perplanet1' in x and ('s_perplanet2a' in x or 's_perplanet2b' in x)
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
class VarietyProduction2aUpgrade(Upgrade):
    name = "s_variety2a"
    resource_type = "gas"
    category = "ships"
    title = "Armada II"
    description = "Train [^2] [Bombers], [^2] [Interceptors], and [^2] [Fighters] over [45 seconds]. [Iron] is [!Frozen] for [20 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'variety', 'parents':['s_variety1']}
    requires = ('s_variety1')

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 45)
        to.add_production(p)
        p = ProductionOrder("bomber", 2, 45)
        to.add_production(p)
        p = ProductionOrder("interceptor", 2, 45)
        to.add_production(p)
        to.owning_civ.frozen.iron += 20

@register_upgrade
class VarietyProduction2bUpgrade(Upgrade):
    name = "s_variety2b"
    resource_type = "gas"
    category = "ships"
    title = "Refit"
    description = "Convert all fighters on a planet into Interceptors and Bombers. [Iron] is [!Frozen] for [60 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'variety', 'parents':['s_variety1']}
    requires = ('s_variety1')     

    def apply(self, to):
        num_fighters = to.ships['fighter']
        for i in range(num_fighters):
            if i % 2 == 0:
                p = ProductionOrder("interceptor", 1, 0.25)
            else:
                p = ProductionOrder("bomber", 1, 0.25)
            to.add_production(p)
        to.ships['fighter'] = 0
        to.owning_civ.frozen.iron += 60

@register_upgrade
class VarietyProduction3Upgrade(Upgrade):
    name = "s_variety3"
    resource_type = "gas"
    category = "ships"
    title = "Refit II"
    description = "Convert all fighters on a planet into Interceptors and Bombers."
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'variety', 'parents':['s_variety2a', 's_variety2b']}
    requires = lambda x: 's_variety1' in x and ('s_variety2a' in x or 's_variety2b' in x)
    infinite = True

    def apply(self, to):
        num_fighters = to.ships['fighter']
        for i in range(num_fighters):
            if i % 2 == 0:
                p = ProductionOrder("interceptor", 1, 0.25)
            else:
                p = ProductionOrder("bomber", 1, 0.25)
            to.add_production(p)
        to.ships['fighter'] = 0        



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
