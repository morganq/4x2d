import random
from upgrade.upgrades import register_upgrade, Upgrade, UPGRADE_CLASSES
from upgrade.building_upgrades import AddBuildingUpgrade, make_simple_stats_building
from productionorder import ProductionOrder
from stats import Stats
from planet import building as buildings

ALIENS = {}

@register_upgrade
class AlienHomeDefenseUpgrade(AddBuildingUpgrade):
    name = "alienhomedefense"
    resource_type = "iron"
    category = "buildings"
    title = "Alien Home Defense"
    description = "Planet fires missiles at nearby enemy ships"
    icon = "mining"
    family = {}
    building = buildings.AlienHomeDefenseBuilding
    requires = None
    alien = True

@register_upgrade
class AlienFighterProductionUpgrade(Upgrade):
    name = "alienfighters"
    resource_type = "iron"
    category = "ships"
    title = "Alien Fighter Production"
    description = "[^3] [Fighters] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien1fighter", 3, 10)
        to.add_production(p)

@register_upgrade
class AlienFighterProductionUpgradeIce(AlienFighterProductionUpgrade):
    name = "alienwarpship"
    resource_type = "ice"
    category = "ships"
    title = "Alien Warpship Production"
    description = "[^1] [Warpship] Over 10 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien1warpship", 3, 10)
        to.add_production(p)

@register_upgrade
class AlienFighterProductionUpgrade(Upgrade):
    name = "alienbattleship"
    resource_type = "gas"
    category = "ships"
    title = "Alien Battleship Production"
    description = "[^1] [Battleship] Over 60 seconds"
    icon = "fighters6"
    requires = None
    alien = True
    infinite = True

    def apply(self, to):
        p = ProductionOrder("alien1battleship", 1, 60)
        to.add_production(p)

@register_upgrade
class AlienTech1Upgrade(Upgrade):
    name = "alientechrof"
    resource_type = "iron"
    category = "tech"
    title = "Alien Tech"
    description = "[Alien Fighters] gain [^+15%] rate of fire"
    icon = "preciseassembly"
    stats = Stats(ship_fire_rate=0.15)
    requires = None
    alien = True
    infinite = True

@register_upgrade
class AlienTech2Upgrade(Upgrade):
    name = "alientechwarp"
    resource_type = "ice"
    category = "tech"
    title = "Alien Tech 2"
    description = "[Alien Fighters] gain [^+2] warp drive"
    icon = "preciseassembly"
    stats = Stats(warp_drive=2)
    requires = None
    alien = True
    infinite = True

@register_upgrade
class AlienTechUpgradeGas(AlienTech1Upgrade):
    resource_type = "gas"    

@register_upgrade
class AlienEconUpgrade(AddBuildingUpgrade):
    name = "alieneconrate"
    resource_type = "iron"
    category = "buildings"
    title = "Refinery"
    description = "[^+15%] [Mining Rate] for [Primary Resource]"
    icon = "refinery"
    requires = None
    alien = True
    building = make_simple_stats_building(stats=Stats(top_mining_rate=0.15), shape="refinery")
    infinite = True

@register_upgrade
class AlienEconUpgradeIce(AddBuildingUpgrade):
    name = "alieneconpop"
    resource_type = "ice"
    category = "buildings"
    title = "Refinery"
    description = "[^+2] max pop"
    icon = "refinery"
    requires = None
    alien = True
    building = make_simple_stats_building(stats=Stats(pop_max_add=2), shape="modulardwellings")
    infinite = True

@register_upgrade
class AlienEconUpgradeGas(AlienEconUpgradeIce):   
    resource_type = "gas"         

class Alien:
    EXPAND_DURATION = 10
    ATTACK_DURATION = 20
    DEFEND_DURATION = 17
    COLONIST = 'alien1colonist'
    name = ""

    def __init__(self, scene, civ):
        self.scene = scene
        self.civ = civ
        self.resource_priority = 'grow'
        self.resource_priority_funs = {
            'grow':self.priority_grow,
            'produce':self.priority_produce,
            'tech':self.priority_tech
        }

        self._last_time = 0
        self.time = 0

    # Returns True if, on this frame, (self.time % duration) just looped over to 0
    def duration_edge(self, duration, offset = 0):
        if ((self.time+offset) % duration) < ((self._last_time+offset) % duration):
            return True
        return False

    def get_resource_priority_odds(self):
        return {
            'grow':0.33,
            'produce':0.33,
            'tech':0.33
        }

    def priority_grow(self, dt):
        pass

    def priority_produce(self, dt):
        pass
    
    def priority_tech(self, dt):
        pass  

    def pick_upgrade_target(self, up):
        return random.choice([p for p in self.scene.get_civ_planets(self.civ)])                

    def update(self, dt):
        self._last_time = self.time
        self.time += dt
        if self.civ.upgrades_stocked:
            offered = self.civ.offer_upgrades(self.civ.upgrades_stocked[0])
            choice = {
                'grow':'buildings',
                'produce':'ships',
                'tech':'tech'
            }[self.resource_priority]
            up = UPGRADE_CLASSES[offered[choice]]
            if choice == 'tech':
                up().apply(self.civ)
            else:
                target = self.pick_upgrade_target(up)
                up().apply(target)

            print("alien researched %s" % up.name)
            
            self.civ.upgrades_stocked.pop(0)
            self.civ.researched_upgrade_names.add(up.name)
            self.civ.clear_offers()            
            self.resource_priority = None
        self.update_resource_priority(dt)
        if self.duration_edge(self.EXPAND_DURATION):
            self.update_expansion()
        if self.duration_edge(self.ATTACK_DURATION):
            self.update_attack()
        if self.duration_edge(self.DEFEND_DURATION):
            self.update_defend()


    def get_expand_chance(self, planet):
        return 0.05 * planet.population

    def get_attack_chance(self, my_planet, target):
        return 0.1

    def get_defend_chance(self, my_planet, target):
        return 0.25

    def get_attacking_ships(self):
        return ['alien1fighter', 'alien1battleship']

    def set_difficulty(self, difficulty):
        self.civ.base_stats['planet_health_mul'] = (difficulty - 1) / 5
        self.civ.base_stats['mining_rate'] = 0.35 + ((difficulty - 1) / 5)
        extra_planets = difficulty // 3
        extra_pops = difficulty % 3
        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.set_health(my_planet.get_max_health(), False)
        my_planet.population += extra_pops

        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - my_planet.pos).sqr_magnitude())
        near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:extra_planets]
        for i in range(extra_planets):
            near_unclaimed[i].change_owner(self.civ)
            near_unclaimed[i].population = extra_pops
            near_unclaimed[i].set_health(near_unclaimed[i].get_max_health(), False)

    def update_expansion(self):
        for planet in self.scene.get_civ_planets(self.civ):
            if planet.population <= 1: continue # Don't empty out one of our planets
            # Randomly, decide to expand
            if random.random() < self.get_expand_chance(planet):
                # Find the neutral planets nearest to this planet
                near_planets = self.scene.get_planets()
                near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
                near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:4] # 4 nearest
                if not near_unclaimed:
                    return
                target = random.choice(near_unclaimed)
                # Figure out how many pop to send
                pop = random.randint(1, planet.population - 1)
                # Emit a colonist
                path = self.scene.pathfinder.find_path(planet, target)
                planet.emit_ship(self.COLONIST, {'to':target, 'path':path, 'num':pop})
                # Figure out if we want to send other ships
                # TODO
    
    def update_attack(self):
        for planet in self.scene.get_civ_planets(self.civ):
            # Find the enemy planets nearest to this planet
            near_planets = self.scene.get_planets()
            near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
            near_enemy = [p for p in near_planets if p.owning_civ and p.owning_civ != self.civ][0:4] # 4 nearest
            if not near_enemy:
                return
            target = random.choice(near_enemy)
            if random.random() < self.get_attack_chance(planet, target):
                path = self.scene.pathfinder.find_path(planet, target)
                for ship_type in self.get_attacking_ships():
                    if ship_type in planet.ships and planet.ships[ship_type] > 0:
                        for i in range(random.randint(1,planet.ships[ship_type])):
                            planet.emit_ship(ship_type, {'to':target, 'path':path})
                if random.random() < 0.66 and planet.population > 1:
                    planet.emit_ship("alien1colonist", {'to':target, 'path':path, 'num':random.randint(1, planet.population-1)})

    def update_defend(self):
        for planet in self.scene.get_civ_planets(self.civ):
            # Find the enemy planets nearest to this planet
            near_planets = self.scene.get_planets()
            near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
            near_ally = [p for p in near_planets if p.owning_civ == self.civ and p is not planet][0:4] # 4 nearest
            if not near_ally:
                return
            target = random.choice(near_ally)
            if random.random() < self.get_defend_chance(planet, target):
                path = self.scene.pathfinder.find_path(planet, target)
                for ship_type in self.get_attacking_ships():
                    if ship_type in planet.ships and planet.ships[ship_type] > 0:
                        for i in range(random.randint(1,planet.ships[ship_type])):
                            planet.emit_ship(ship_type, {'to':target, 'path':path})

        
    def update_resource_priority(self, dt):
        # Determine new resource priority
        if self.resource_priority is None:
            odds = self.get_resource_priority_odds()
            total_chance = 0
            for op, chance in odds.items():
                if random.random() < total_chance + chance:
                    self.resource_priority = op
                    break
                else:
                    total_chance += chance
            else:
                self.resource_priority = list(odds.keys())[-1]
        else:
            self.resource_priority_funs[self.resource_priority](dt)

    def render(self, screen):
        pass