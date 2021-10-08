import random

from upgrade.upgrades import UPGRADE_CLASSES

from aliens import buildorder

ALIENS = {}


# New update
# figure out where we are in the BO
# 

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
        self.civ.color = self.COLOR
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
        self.redistribute_timer = 0
        self.near_winning = False

    # Expand: figure out a target planet and a source planet, then send ships
    def execute_expand(self, target_type = None):
        all_potential_targets = self.scene.get_civ_planets(None)
        sorted_targets = all_potential_targets[::]

        # Find a target
        if target_type == buildorder.BOExpand.TARGET_TYPE_NEAR_HOME:
            sorted_targets.sort(key=lambda p:(p.pos - self.civ.homeworld.pos).sqr_magnitude())

        elif target_type == buildorder.BOExpand.TARGET_TYPE_NEAR_ENEMY:
            sorted_targets.sort(key=lambda p:(p.pos - self.scene.player_civ.homeworld.pos).sqr_magnitude())

        elif target_type == buildorder.BOExpand.TARGET_TYPE_MIDDLE:
            def key(p):
                # Middle = smallest delta between near me and near enemy distances.
                d1 = (p.pos - self.scene.player_civ.homeworld.pos).sqr_magnitude()
                d2 = (p.pos - self.civ.homeworld.pos).sqr_magnitude()
                return abs(d1 - d2)
            sorted_targets.sort(key=key)

        elif target_type == buildorder.BOExpand.TARGET_TYPE_RANDOM:
            random.shuffle(sorted_targets)

        # TODO: add a bit of randomness?
        target = sorted_targets[0]

        # Sort potential expand-from planets
        all_potential_sources = self.scene.get_civ_planets(self.civ)
        all_potential_sources = [p for p in all_potential_sources if p.population > 1]
        sorted_sources = all_potential_sources[::]
        sorted_sources.sort(key=lambda p:(p.pos - target.pos).sqr_magnitude())

        # TODO: randomness?
        source = sorted_sources[0]
        self.send_expansion_party(source, target)

    # Send some pop on a colonist ship and possibly send some defenders
    def send_expansion_party(self, source, target):
        if random.random() < 0.33:
            pop = random.randint(1, max(source.population // 2,1))
        else:
            pop = 1
        source.emit_ship(self.get_colonist(), {'to':target, 'num':pop})

        if random.random() < 0.5:
            ships = self.get_planet_ship_instances(source)
            num_to_send = random.randint(1, max(len(ships) // 2,1))
            for s in ships[0:num_to_send]:
                source.emit(s, {'to':target})

    def get_planet_ship_instances(self, planet):
        ships = []
        for name in planet.ships.keys():
            for i in range(planet.ships[name]):
                ships.append(name)
        return ships

    def get_build_order_steps(self):
        return []

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
        avail = [p for p in self.scene.get_civ_planets(self.civ) if p.is_buildable()]
        if avail:
            return random.choice(avail)
        else:
            return None

    def count_ships(self, civ):
        ships = 0
        for planet in self.scene.get_civ_planets(civ):
            ships += sum(planet.ships.values())
        for s in self.scene.get_civ_ships(civ):
            if s.SHIP_BONUS_NAME != "colonist":
                ships += 1
        return ships

    def check_fear_attack(self):
        if self.difficulty <= 2:
            self.fear_attack = False
            return

        mine = self.count_ships(self.civ)
        enemys = self.count_ships(self.scene.player_civ)
        if enemys > mine * 1.33:
            self.fear_attack = True
        else:
            self.fear_attack = False

    def update(self, dt):
        self._last_time = self.time
        self.time += dt
        if self.civ.upgrades_stocked:
            self.resource_priority = None
            self.update_resource_priority(dt)
            offered = self.civ.offer_upgrades(self.civ.upgrades_stocked[0], lambda x:x.alien_name == self.name)
            bo_step = self.build_order.get_current_step(self.time)
            up = None
            if bo_step and bo_step.name == "research":
                if bo_step.asset in list(offered.values()):
                    up = UPGRADE_CLASSES[bo_step.asset]
                    self.build_order.completed_current_step()
            if not up:
                choice = {
                    'grow':'buildings',
                    'produce':'ships',
                    'tech':'tech'
                }[self.resource_priority]
                up = UPGRADE_CLASSES[offered[choice]]

            if self.difficulty >= up.alien_min_level:
                if up.category == 'tech':
                    up().apply(self.civ)
                else:
                    target = self.pick_upgrade_target(up)
                    if target is not None: # If we have none avail... who cares, just skip this upgrade.
                        up().apply(target)

                print("alien researched %s" % up.name)
            else:
                print("alien wanted to research %s but it's not allowed at this level" % up.name)
            
            self.civ.upgrades_stocked.pop(0)
            self.civ.researched_upgrade_names.add(up.name)
            self.civ.upgrades.append(up)
            self.civ.clear_offers()     
               
        if self.duration_edge(self.EXPAND_DURATION):
            self.update_expansion()

        attack_duration = self.ATTACK_DURATION
        if self.near_winning:
            attack_duration = 1
        if self.duration_edge(attack_duration):
            self.update_attack()

        if self.duration_edge(self.DEFEND_DURATION):
            self.update_defend()

        if self.duration_edge(20):
            for fleet in self.scene.fleet_managers['enemy'].current_fleets:
                if fleet.is_waiting():
                    self.scene.fleet_managers['enemy'].recall_fleet(fleet)

        if self.duration_edge(5):
            self.check_fear_attack()

        if self.redistribute_timer <= 0:
            self.redistribute_excess_ships()
        self.redistribute_timer -= dt

        if self.duration_edge(5) and self.time > 90:
            if len(self.scene.get_civ_planets(self.civ)) > len(self.scene.get_civ_planets(self.scene.player_civ)) + 1:
                print("Near winning!")
                self.near_winning = True
            else:
                self.near_winning = False

    def redistribute_excess_ships(self):
        all_my_planets = self.scene.get_civ_planets(self.civ)
        random.shuffle(all_my_planets)
        for planet in all_my_planets:
            sent = False
            total_ships = sum(planet.ships.values())
            max_ships = planet.get_max_ships()
            if total_ships > max_ships:
                other_planets = all_my_planets[::]
                other_planets.remove(planet)
                if other_planets:
                    other = random.choice(other_planets)
                    d = total_ships - max_ships
                    for i in range(d):
                        possible_ships = [k for k in self.get_attacking_ships() if planet.ships[k] > 0]
                        if possible_ships:
                            randomship = random.choice(possible_ships)
                            planet.emit_ship(randomship, {'to': other})
                            sent = True
                    if sent:
                        self.redistribute_timer = random.randint(25, 50)
                        return # just one transfer per round
                    
    @classmethod
    def get_quote(kls):
        return random.choice(kls.quotes)

    def get_expand_chance(self, planet):
        return 0.05 * planet.population

    def get_attack_chance(self, my_planet, target):
        return 0.1

    def get_defend_chance(self, my_planet, target):
        return 0.25

    def get_attacking_ships(self):
        return []

    def get_max_attackers(self):
        curve = {
            1: 0,
            2: 2,
            3: 3,
            4: 3,
            5: 4,
            6: 6,
        }.get(self.difficulty, 999)        

        if self.difficulty > 1 and self.time > 300:
            curve *= 2

        return curve

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.civ.base_stats['planet_health_mul'] = -0.5 + (difficulty - 1) / 4
        self.civ.base_stats['mining_rate'] = 0.75 #-0.5 + ((difficulty - 1) / 6)
        #self.civ.base_stats['max_ships_mul'] = min(-0.55 + (difficulty - 1) / 10,0)
        self.civ.base_stats['max_ships_per_planet'] = int((difficulty + 5) / 2)
        extra_planets = 0
        if difficulty == 7: extra_planets = 1
        if difficulty == 8: extra_planets = 2
        if difficulty == 9: extra_planets = 4
        extra_pops = difficulty // 2
        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.population += extra_pops

        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - my_planet.pos).sqr_magnitude())
        near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:extra_planets]
        for i in range(extra_planets):
            near_unclaimed[i].change_owner(self.civ)
            near_unclaimed[i].population = extra_pops
            near_unclaimed[i].set_health(near_unclaimed[i].get_max_health(), False)

        for planet in self.scene.get_civ_planets(self.civ):
            planet.set_health(planet.get_max_health(), False)            

        self.build_order = buildorder.BuildOrder(self.get_build_order_steps())

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

    def count_attacking_ships(self):
        c = 0
        for ship in self.scene.get_civ_ships(self.civ):
            if ship.SHIP_BONUS_NAME == "colonist" and ship.chosen_target.owning_civ == self.scene.player_civ:
                c += 1
        for planet in self.scene.get_civ_planets(self.civ):
            for ship_type, emit_data in planet.emit_ships_queue:
                targets_enemy = emit_data['to'].owning_civ and emit_data['to'].owning_civ != self.civ
                if ship_type in self.get_attacking_ships() and targets_enemy:
                    c += 1

        return c

    def count_expanding_ships(self):
        colonists_out = 0
        for ship in self.scene.get_civ_ships(self.civ):
            if ship.SHIP_BONUS_NAME == "colonist":
                colonists_out += 1
        return colonists_out        
                

    def update_attack(self):
        for planet in self.scene.get_civ_planets(self.civ):
            # Find the enemy planets nearest to this planet
            near_enemy = self._get_possible_attack_targets(planet)
            if not near_enemy:
                return
            target = random.choice(near_enemy)
            if random.random() < self.get_attack_chance(planet, target):
                num_attackers = 0
                sent = False
                for ship_type in self.get_attacking_ships():
                    if ship_type in planet.ships and planet.ships[ship_type] > 0:
                        for i in range(planet.ships[ship_type]):
                            if num_attackers + self.count_attacking_ships() >= self.get_max_attackers():
                                break
                            planet.emit_ship(ship_type, {'to':target})
                            num_attackers += 1
                            sent = True
                            self.last_attack_time = self.time
                            if not self.build_order.is_over():
                                bostep = self.build_order.get_current_step(self.time)
                                if bostep and bostep.name == "attack":   
                                    self.build_order.completed_current_step()                         
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
