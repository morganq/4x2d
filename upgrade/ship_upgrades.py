import random

import ships
from productionorder import ProductionOrder

from upgrade.upgrades import Upgrade, register_upgrade


@register_upgrade
class InstantFighters1Upgrade(Upgrade):
    name = "s_instantfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Fighter Rush Order"
    description = "Train [^1] [Fighter] Over 20 seconds"
    icon = "fighterrush1"
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
    title = "Fighter Rush Order II"
    description = "Train [^2] [Fighters] over 20 seconds"
    icon = "fighterrush2"
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
    title = "Emergency Fighters"
    description = "Train [^2] [Fighters] [^Instantly], Iron is [!Frozen] for 15 seconds."
    icon = "emergencyfighters1"
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
    title = "Emergency Fighters II"
    description = "Train [^4] [Fighters] [^Instantly], [!-2] population"
    icon = "emergencyfighters2"
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
    title = "Fighter Assembly"
    description = "Train [^2] [Fighters] over 120 seconds. "
    icon = "fighterassembly1"
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
    title = "Fighter Support"
    description = "Train [^3] [Fighters] over 120 seconds. [^+100] [Ice]"
    icon = "fightersupport1"
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
    title = "Fighter Assembly II"
    description = "Train [^3] [Fighters] over 200 seconds."
    icon = "fighterassembly2"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 200)
        to.add_production(p)        

@register_upgrade
class LongFighters3Upgrade(Upgrade):
    name = "s_longfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Fighter Support II"
    description = "Train [^4] [Fighters] over 240 seconds. [^+50] [Gas]"
    icon = "fightersupport2"
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
    title = "Scout Construction"
    description = "Train [^1] [Scout] over 10 seconds"
    icon = "scoutconstruction1"
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
    title = "Scout Workshop"
    description = "Train [^1] [Scout] over 60 seconds for every 2 [Workers]. "
    icon = "scoutworkshop"
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
    title = "Scout Construction II"
    description = "Train [^2] [Scouts] over 30 seconds"
    icon = "scoutconstruction2"
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
    title = "Scout Construction III"
    description = "Train [^2] [Scouts] over 10 seconds"
    icon = "scoutconstruction3"
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
    description = "Every in-flight ship warps into range of its target and gains [^+33%] Attack Speed for 6 seconds"
    icon = "fleetwarp1"
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
    description = "Every in-flight ship is [^fully repaired], warps into range of its target, and gains [^+33%] Attack Speed for 6 seconds"
    icon = "fleetwarp2"
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
    title = "Fleet Warp III"
    description = "Every in-flight ship warps into range of its target, and gains [^+33%] Attack Speed for 6 seconds. Add a [Worker Ship] with population [^3] to a random fleet"
    icon = "fleetwarp3"
    cursor = None
    family = {'tree':'warp', 'parents':['s_warp1']}
    requires = ('s_warp1',)

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.command_warp()        
        fm = to.scene.get_fleet_manager(to)
        if fm.current_fleets:
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
    title = "Fleet Rescue"
    description = "All in-flight ships other than [Fighters] gain [^15] [Shield]"
    icon = "fleetrescue"
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
    title = "Interceptor Order"
    description = "Train [^1] [Interceptor] over 10 seconds"
    icon = "interceptororder1"
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
    title = "Interceptor Order II"
    description = "Train [^2] [Interceptors] over 45 seconds"
    icon = "interceptororder2"
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
    title = "Interceptor Blueprint"
    description = "Train [^3] [Interceptors] at random planets over 20 seconds"
    icon = "interceptorblueprint"
    cursor = None
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
    title = "Interceptor Rush Order"
    description = "Train [^2] [Interceptors] instantly"
    icon = "interceptorrushorder"
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
    description = "Train [^2] [Bombers] over 60 seconds"
    icon = "bombersquadron1"
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
    description = "Train [^3] [Bombers] over 60 seconds"
    icon = "bombersquadron2"
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
    description = "Train [^2] [Bombers] over 45 seconds, [^+150] [Iron]"
    icon = "bombsupport1"
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
    description = "Train [^3] [Bombers] over 60 seconds, [^+75] [Gas]"
    icon = "bombsupport2"
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
    title = "Blueprint Uplink"
    description = "Train [^1] [Interceptor] and [^1] [Bomber] over 60 seconds at random planets"
    icon = "blueprintuplink1"
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
    title = "Instant Uplink"
    description = "Train [^1] [Fighter], [^1] [Interceptor], and [^1] [Bomber] instantly at random planets"
    icon = "instantuplink"
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
    title = "Blueprint Uplink II"
    description = "Train [^2] [Fighters], [^1] [Interceptor], and [^1] [Bomber] over 60 seconds at random planets"
    icon = "blueprintuplink2"
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
    title = "Scavenge Parts"
    description = "Train [^1] [Interceptor] and [^1] [Bomber] instantly at your newest planet"
    icon = "scavengeparts"
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
    description = "Train [^1] [Battleship] over 60 seconds"
    icon = "battleship1"
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
    description = "Train [^1] [Battleship] over 30 seconds"
    icon = "battleship2"
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
    description = "Train [^1] [Battleship] [^instantly]. [!Freeze] [Gas] for 15 seconds"
    icon = "emergencybattleship"
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
    description = "Train [^2] [Battleships] over 60 seconds"
    icon = "battleshippair"
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
    description = "Train [^1] [Fighter] over 60 seconds at each planet"
    icon = "planetaryguard"
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
    title = "Scouting Fleet"
    description = "Train [^1] [Scout] over 30 seconds at each planet"
    icon = "surveyfleet"
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
    description = "Train [^1] [Fighter] over 20 seconds at each planet"
    icon = "planetaryguard2"
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
    description = "Train [^1] [Fighter] over 10 seconds at each planet"
    icon = "planetaryguard3"
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
    description = "Train [^2] [Bombers] and [^2] [Interceptors] over 45 seconds. [Iron] is [!Frozen] for 30 seconds"
    icon = "armada1"
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
    description = "Train [^2] [Bombers], [^2] [Interceptors], and [^2] [Fighters] over 45 seconds. [Iron] is [!Frozen] for 30 seconds"
    icon = "armada2"
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
    icon = "refit1"
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
    icon = "refit2"
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
