import random
from upgrade.upgrades import UPGRADE_CLASSES

ALIENS = {}

class Alien:
    EXPAND_DURATION = 10
    EXPAND_NUM_NEAREST = 2
    ATTACK_DURATION = 20
    DEFEND_DURATION = 17
    name = ""
    title = ""
    tips = []

    def __init__(self, scene, civ):
        self.scene = scene
        self.civ = civ
        self.civ.alien = self
        self.resource_priority = 'grow'
        self.resource_priority_funs = {
            'grow':self.priority_grow,
            'produce':self.priority_produce,
            'tech':self.priority_tech
        }
        self.difficulty = 0

        self._last_time = 0
        self.last_attack_time = 0
        self.time = 0
        self.fear_attack = False

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

    def count_ships(self, civ):
        ships = 0
        for planet in self.scene.get_civ_planets(civ):
            ships += sum(planet.ships.values())
        for s in self.scene.get_civ_ships(civ):
            if s.SHIP_BONUS_NAME != "colonist":
                ships += 1
        return ships

    def check_fear_attack(self):
        mine = self.count_ships(self.civ)
        enemys = self.count_ships(self.scene.my_civ)
        if enemys > mine * 1.33:
            print("in fear", mine, enemys)
            self.fear_attack = True
        else:
            print("feelin safe", mine, enemys)
            self.fear_attack = False

    def update(self, dt):
        self._last_time = self.time
        self.time += dt
        if self.civ.upgrades_stocked:
            self.resource_priority = None
            self.update_resource_priority(dt)
            offered = self.civ.offer_upgrades(self.civ.upgrades_stocked[0], lambda x:x.alien_name == self.name)
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
            self.civ.upgrades.append(up)
            self.civ.clear_offers()            
        if self.duration_edge(self.EXPAND_DURATION):
            self.update_expansion()
        if self.duration_edge(self.ATTACK_DURATION):
            self.update_attack()
        if self.duration_edge(self.DEFEND_DURATION):
            self.update_defend()

        if self.duration_edge(10):
            for fleet in self.scene.fleet_managers['enemy'].current_fleets:
                if fleet.is_waiting():
                    self.scene.fleet_managers['enemy'].recall_fleet(fleet)

        if self.duration_edge(5):
            self.check_fear_attack()

    def get_expand_chance(self, planet):
        return 0.05 * planet.population

    def get_attack_chance(self, my_planet, target):
        return 0.1

    def get_defend_chance(self, my_planet, target):
        return 0.25

    def get_attacking_ships(self):
        return []

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.civ.base_stats['planet_health_mul'] = (difficulty - 1) / 4
        self.civ.base_stats['mining_rate'] = 0.35 + ((difficulty - 1) / 4)
        extra_planets = difficulty // 2
        extra_pops = difficulty // 2
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
                near_unclaimed = self._get_possible_expand_targets(planet)
                if not near_unclaimed:
                    return
                target = random.choice(near_unclaimed)
                # Figure out how many pop to send
                if random.random() < 0.33:
                    pop = random.randint(1, planet.population // 2)
                else:
                    pop = 1
                # Emit a colonist
                planet.emit_ship(self.get_colonist(), {'to':target, 'num':pop})
                # Figure out if we want to send other ships
                # TODO
    
    def _get_possible_expand_targets(self, planet):
        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
        near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:self.EXPAND_NUM_NEAREST]

        return near_unclaimed

    def _get_possible_attack_targets(self, planet):
        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
        near_enemy = [p for p in near_planets if p.owning_civ and p.owning_civ != self.civ][0:2] # 2 nearest    
        
        return near_enemy    

    def update_attack(self):
        for planet in self.scene.get_civ_planets(self.civ):
            # Find the enemy planets nearest to this planet
            near_enemy = self._get_possible_attack_targets(planet)
            if not near_enemy:
                return
            target = random.choice(near_enemy)
            if random.random() < self.get_attack_chance(planet, target):
                sent = False
                for ship_type in self.get_attacking_ships():
                    if ship_type in planet.ships and planet.ships[ship_type] > 0:
                        for i in range(planet.ships[ship_type]):
                            planet.emit_ship(ship_type, {'to':target})
                            sent = True
                            self.last_attack_time = self.time
                if sent and random.random() < 0.5 and planet.population > 1:
                    planet.emit_ship(self.get_colonist(), {'to':target, 'num':random.randint(1, planet.population-1)})

    def get_colonist(self):
        return ""

    def update_defend(self):
        for planet in self.scene.get_civ_planets(self.civ):
            # Find the enemy planets nearest to this planet
            near_planets = self.scene.get_planets()
            near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
            near_ally = [p for p in near_planets if p.owning_civ == self.civ and p is not planet]
            if not near_ally:
                return
            target = random.choice(near_ally)
            if random.random() < self.get_defend_chance(planet, target):
                for ship_type in self.get_attacking_ships():
                    if ship_type in planet.ships and planet.ships[ship_type] > 0:
                        for i in range(planet.ships[ship_type]):
                            planet.emit_ship(ship_type, {'to':target})

        
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