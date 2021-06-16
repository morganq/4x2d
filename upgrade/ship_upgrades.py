from upgrade.upgrades import register_upgrade, Upgrade
from productionorder import ProductionOrder
import ships

@register_upgrade
class Basic1Upgrade(Upgrade):
    name = "s_basicfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Standard Order"
    description = "Train [^3] [Fighters] Over [30 seconds]"
    icon = "standardorder"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 30)
        to.add_production(p)

@register_upgrade
class Basic2Upgrade(Upgrade):
    name = "s_basicfighters2"
    resource_type = "iron"
    category = "ships"
    title = "Expedited Order"
    description = "Train [^3] [Fighters] Over [25 seconds]"
    icon = "expeditedorder"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':['s_basicfighters1']}
    requires = ('s_basicfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 25)
        to.add_production(p)  

@register_upgrade
class Basic3Upgrade(Upgrade):
    name = "s_basicfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Rush Order"
    description = "Train [^3] [Fighters] Over [20 seconds]"
    icon = "rushorder"
    cursor = "allied_planet"
    family = {'tree':'basicfighters', 'parents':['basicfighters2']}
    requires = ('s_basicfighters1', 's_basicfighters2')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 20)
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
    description = "Train [^2] [Fighters] [^Instantly], Planet loses [!25] health"
    icon = "warmanufacturing"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters1']}
    requires = ('s_instantfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 2, 0.25)
        to.add_production(p)        
        to.health -= 25

@register_upgrade
class InstantFighters3aUpgrade(Upgrade):
    name = "s_instantfighters3a"
    resource_type = "iron"
    category = "ships"
    title = "Guard Deployment II"
    description = "Train [^3] [Fighters] [^Instantly], [!-3] population"
    icon = "guarddeployment2"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters2a']}
    requires = ('s_instantfighters1','s_instantfighters2a')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.population -= 3    

@register_upgrade
class InstantFighters3bUpgrade(Upgrade):
    name = "s_instantfighters3b"
    resource_type = "iron"
    category = "ships"
    title = "War Manufacturing II"
    description = "Train [^3] [Fighters] [^Instantly], Planet loses [!35] health"
    icon = "warmanufacturing2"
    cursor = "allied_planet"
    family = {'tree':'instantfighters', 'parents':['s_instantfighters2b']}
    requires = ('s_instantfighters1','s_instantfighters2b')
    infinite = True

    def apply(self, to):
        p = ProductionOrder("fighter", 3, 0.25)
        to.add_production(p)        
        to.health -= 35

@register_upgrade
class LongFighters1Upgrade(Upgrade):
    name = "s_longfighters1"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly"
    description = "Train [^4] [Fighters] Over [120 seconds], [^+50] Iron"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':[]}

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 120)
        to.add_production(p)        
        to.owning_civ.resources.iron += 50

@register_upgrade
class LongFighters2aUpgrade(Upgrade):
    name = "s_longfighters2a"
    resource_type = "iron"
    category = "ships"
    title = "Strategic Assembly"
    description = "Train [^5] [Fighters] Over [120 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 5, 120)
        to.add_production(p)

@register_upgrade
class LongFighters2bUpgrade(Upgrade):
    name = "s_longfighters2b"
    resource_type = "iron"
    category = "ships"
    title = "Efficient Assembly II"
    description = "Train [^4] [Fighters] Over [120 seconds], [^+100] Iron"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'longfighters', 'parents':['s_longfighters1']}
    requires = ('s_longfighters1',)

    def apply(self, to):
        p = ProductionOrder("fighter", 4, 120)
        to.add_production(p)        
        to.owning_civ.resources.iron += 100

@register_upgrade
class LongFighters3Upgrade(Upgrade):
    name = "s_longfighters3"
    resource_type = "iron"
    category = "ships"
    title = "Recycled Armaments"
    description = "Train [^5] [Fighters] Over [120 seconds], [^+50] Gas"
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
    description = "Every ship warps towards its target and gains [^+67%] attack speed for [6 seconds]"
    icon = "ship_default"
    cursor = None
    family = {'tree':'warp', 'parents':[]}
    infinite = True

    def apply(self, to):
        for ship in to.scene.get_civ_ships(to):
            ship.command_warp()

#### ICE ####

@register_upgrade
class Interceptors1Upgrade(Upgrade):
    name = "s_basicinterceptors1"
    resource_type = "ice"
    category = "ships"
    title = "Interceptors"
    description = "Train [^2] [Interceptors] Over [45 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicinterceptors', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("interceptor", 2, 45)
        to.add_production(p)

@register_upgrade
class Bombers1Upgrade(Upgrade):
    name = "s_basicbombers1"
    resource_type = "ice"
    category = "ships"
    title = "Bombers"
    description = "Train [^2] [Bombers] Over [45 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbombers', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("bomber", 2, 45)
        to.add_production(p)       

@register_upgrade
class HangarProduction1Upgrade(Upgrade):
    name = "s_hangarprod1"
    resource_type = "ice"
    category = "ships"
    title = "Specialized Manufacturing"
    description = "Train [^1] ship [^instantly] at each hangar"
    icon = "ship_default"
    cursor = None
    family = {'tree':'hangarprod', 'parents':[]}
    infinite = True

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            for building in planet.buildings:
                if building['building'].upgrade.name == "b_hangar1":
                    planet.add_ship("fighter")
                elif building['building'].upgrade.name == "b_hangar2a":
                    planet.add_ship("interceptor")
                elif building['building'].upgrade.name == "b_hangar2b":
                    planet.add_ship("bomber")                    
                elif building['building'].upgrade.name == "b_hangar3":
                    planet.add_ship("battleship")


### GAS ####

@register_upgrade
class Battleships1Upgrade(Upgrade):
    name = "s_basicbattleships1"
    resource_type = "gas"
    category = "ships"
    title = "Battleships"
    description = "Train [^1] [Battleship] Over [30 seconds]"
    icon = "ship_default"
    cursor = "allied_planet"
    family = {'tree':'basicbattleships', 'parents':[]}
    infinite = True

    def apply(self, to):
        p = ProductionOrder("battleship", 1, 30)
        to.add_production(p)         

@register_upgrade
class PerPlanetProduction1Upgrade(Upgrade):
    name = "s_perplanet1"
    resource_type = "gas"
    category = "ships"
    title = "Planetary Guard"
    description = "Train [^1] [Fighter] over [20 seconds] at each planet"
    icon = "ship_default"
    cursor = None
    family = {'tree':'perplanet', 'parents':[]}
    infinite = True

    def apply(self, to):
        for planet in to.scene.get_civ_planets(to):
            planet.add_production(ProductionOrder("fighter", 1, 20))

@register_upgrade
class AddColonistProduction1Upgrade(Upgrade):
    name = "s_addcolonist1"
    resource_type = "gas"
    category = "ships"
    title = "Civilian Convoy"
    description = "Add a [^1] population [Worker] ship to up to 3 random fleets"
    icon = "ship_default"
    cursor = None
    family = {'tree':'addcolonist', 'parents':[]}
    infinite = True

    def apply(self, to):
        for fleet in to.scene.fleet_managers['my'].current_fleets[0:3]:
            pos, rad = fleet.get_size_info()
            s = ships.colonist.Colonist(to.scene, pos, to)
            s.set_pop(1)
            s.set_target(fleet.ships[0].chosen_target)
            to.scene.game_group.add(s)



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