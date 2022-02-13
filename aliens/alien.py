import math
import random

import planet
from debug import print
from intel.inteldata import IntelManager
from upgrade.upgrades import UPGRADE_CLASSES

from aliens import bossmothership, buildorder

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
        self.civ.color = self.COLOR
        self.difficulty = 0

        self._last_time = 0
        self.last_attack_time = 0
        self.time = 0
        self.defend_countdown = self.get_defend_countdown()
        self.attack_countdown = 20
        self.fear_attack = False
        self.redistribute_timer = 0
        self.near_winning = False

        self.time_behind_expand_curve = 0

        self.build_order_acceleration = 1
        self.attack_behind_expansion_curve_countdown = 30

    # Merge the planets' emit queue ships and in-world ships. Optionally filter.
    # Returns [(ship_name, target), ...]
    def get_ordered_ships(self, ship_filter=None, target_filter=None):
        all_ships = []
        for planet in self.scene.get_civ_planets(self.civ):
            all_ships.extend([
                (ship_name, data['to']) for (ship_name, data) in planet.emit_ships_queue
            ])
        for ship in self.scene.get_civ_ships(self.civ):
            all_ships.append((ship.SHIP_NAME, ship.chosen_target))

        if ship_filter:
            all_ships = [s for s in all_ships if s[0] == ship_filter]

        if target_filter:
            all_ships = [s for s in all_ships if s[1] == target_filter]

        return all_ships

    # Expand: figure out a target planet and a source planet, then send ships
    def execute_expand(self, target_type):
        if self.count_expansions_plus_pending() >= self.get_max_planets():
            return False
        all_potential_targets = self.scene.get_civ_planets(None)
        # Eliminate targets that already have colonists heading towards them
        all_potential_targets = [
            t for t in all_potential_targets
            if len(self.get_ordered_ships(self.get_colonist(), t)) == 0
        ]
        sorted_targets = all_potential_targets[::]

        # Find a target
        if target_type == buildorder.BOExpand.TARGET_TYPE_NEAR_HOME:
            sorted_targets.sort(key=lambda p:(p.pos - self.civ.homeworld.pos).length_squared())

        elif target_type == buildorder.BOExpand.TARGET_TYPE_NEAR_ENEMY:
            sorted_targets.sort(key=lambda p:(p.pos - self.scene.player_civ.homeworld.pos).length_squared())

        elif target_type == buildorder.BOExpand.TARGET_TYPE_MIDDLE:
            def key(p):
                # Middle = smallest delta between near me and near enemy distances.
                d1 = (p.pos - self.scene.player_civ.homeworld.pos).length_squared()
                d2 = (p.pos - self.civ.homeworld.pos).length_squared()
                return abs(d1 - d2)
            sorted_targets.sort(key=key)

        elif target_type == buildorder.BOExpand.TARGET_TYPE_RANDOM:
            random.shuffle(sorted_targets)

        if not sorted_targets:
            return False

        # TODO: add a bit of randomness?
        target = sorted_targets[0]

        # Sort potential expand-from planets
        all_potential_sources = self.scene.get_civ_planets(self.civ)
        all_potential_sources = [p for p in all_potential_sources if p.population > 1]
        sorted_sources = all_potential_sources[::]
        sorted_sources.sort(key=lambda p:(p.pos - target.pos).length_squared())

        
        if not sorted_sources:
            return False

        # TODO: randomness?
        source = sorted_sources[0]
        self.send_expansion_party(source, target)
        return True

    # Send some pop on a colonist ship and possibly send some defenders
    def send_expansion_party(self, source, target):
        if random.random() < 0.33:
            pop = random.randint(1, max(source.population // 2,1))
        else:
            pop = 1
        source.emit_ship(self.get_colonist(), {'to':target, 'num':pop})

        if random.random() < 0.5:
            ships = [
                s for s in self.get_planet_ship_instances(source)
                if s in self.get_attacking_ships()
            ]
            num_to_send = random.randint(1, max(len(ships) // 2,1))
            for s in ships[0:num_to_send]:
                source.emit_ship(s, {'to':target})

    def execute_research(self, asset_name, target_type):
        uc = UPGRADE_CLASSES[asset_name]
        if uc.alien_min_level > self.difficulty:
            return False
        if uc.resource_type in self.civ.upgrades_stocked:
            self.civ.upgrades_stocked.remove(uc.resource_type)
            #if uc.cursor is None: # TODO: add cursor to every tech??
            if uc.category == "tech":
                self.research_with_target(asset_name, self.civ)
            else:
                target = None
                available_planets = [
                    p for p in self.scene.get_civ_planets(self.civ)
                    if p.is_buildable()
                ]

                if not available_planets:
                    return False

                # Random planet
                if target_type == buildorder.BOResearch.TARGET_TYPE_RANDOM:
                    target = random.choice(available_planets)

                # Planet which lacks the building
                elif target_type == buildorder.BOResearch.TARGET_TYPE_LACKING_ASSET:
                    def key(p):
                        return asset_name in [b['building'].upgrade.name for b in p.buildings]
                    available_planets.sort(key=key)
                    print([(p, key(p)) for p in available_planets])
                    target = available_planets[0]

                # Homeworld, or random if dead
                elif target_type == buildorder.BOResearch.TARGET_TYPE_HOMEWORLD:
                    if self.civ.homeworld in available_planets:
                        target = self.civ.homeworld
                    else:
                        target = random.choice(available_planets)

                # Undefended
                elif target_type == buildorder.BOResearch.TARGET_TYPE_UNDEFENDED:
                    available_planets.sort(key=lambda p:sum(p.ships.values()))
                    target = available_planets[0]

                if target is None:
                    return False

                self.research_with_target(asset_name, target)
                    
            return True
        else:
            return False
        
    def research_with_target(self, asset_name, target):
        print("Researching %s" % asset_name)
        up = UPGRADE_CLASSES[asset_name]
        up().apply(target)
        self.civ.register_research(up.name)
        self.civ.upgrades.append(up)        

    def execute_attack(self, attack_type, attack_strength=1):
        all_potential_targets = self.scene.get_civ_planets(self.scene.player_civ)
        all_potential_targets = [
            t for t in all_potential_targets
            if len(self.get_ordered_ships(target_filter=t)) <= self.get_max_attackers() * attack_strength
        ]
        if not all_potential_targets:
            return False

        sorted_targets = all_potential_targets[::]

        all_potential_sources = self.scene.get_civ_planets(self.civ)
        all_potential_sources = [
            s for s in all_potential_sources
            if sum(
                {k:v for k,v in s.ships.items() if k in self.get_attacking_ships()}
            .values()) > 0
        ]
        all_potential_ships = sum([
            sum(
                {k:v for k,v in s.ships.items() if k in self.get_attacking_ships()}
            .values())            
            for s in all_potential_sources
        ])
        num_to_send = math.ceil(all_potential_ships * attack_strength)
        possible_colonist = True
        if attack_strength < 0.25:
            possible_colonist = False
        print("num to send", num_to_send)

        if not all_potential_sources:
            return False

        sorted_sources = all_potential_sources[::]

        if attack_type == buildorder.BOAttack.ATTACK_TYPE_CENTRAL:
            sorted_targets.sort(key=lambda p:p.population, reverse=True)
            target = sorted_targets[0]

            sorted_sources.sort(key=lambda p:(p.pos - target.pos).length_squared())
            num_sources = random.randint(2,4)
            sources = sorted_sources[0:num_sources]
            for source in sources:
                self.send_attacking_party(source, target, num_to_send, possible_colonist)

        elif attack_type == buildorder.BOAttack.ATTACK_TYPE_OUTLYING:
            def key(p):
                # Middle = smallest delta between near me and near enemy distances.
                d1 = (p.pos - self.scene.player_civ.homeworld.pos).length_squared()
                d2 = (p.pos - self.civ.homeworld.pos).length_squared()
                return abs(d1 - d2)

            sorted_targets.sort(key=key)
            target = sorted_targets[0]
            sorted_sources.sort(key=lambda p:(p.pos - target.pos).length_squared())
            self.send_attacking_party(sorted_sources[0], target, num_to_send, possible_colonist)

        elif attack_type == buildorder.BOAttack.ATTACK_TYPE_RANDOM:
            target = random.choice(sorted_targets)
            sorted_sources.sort(key=lambda p:(p.pos - target.pos).length_squared())
            self.send_attacking_party(sorted_sources[0], target, num_to_send, possible_colonist)

        return True

    def send_attacking_party(self, source, target, max_num = 999, possible_colonist=True):
        ships = self.get_planet_ship_instances(source)
        ships = [s for s in ships if s in self.get_attacking_ships()]
        num_to_send = random.randint(1, max(len(ships),1))
        num_to_send = min(num_to_send, max_num)
        num_attackers = len(self.get_ordered_ships(target_filter=target))
        num_to_send = min(num_to_send, self.get_max_attackers() - num_attackers)
        print("attacking with %d" % num_to_send)
        if num_to_send <= 0:
            return
        for s in ships[0:num_to_send]:
            source.emit_ship(s, {'to':target})
        
        num_planets = self.count_expansions_plus_pending()
        if ships and possible_colonist and num_planets < self.get_max_planets():
            if source.population > 1 and random.random() < 0.8:
                source.emit_ship(self.get_colonist(), {'to':target, 'num':1})

    def count_expansions_plus_pending(self):
        current = len(self.scene.get_civ_planets(self.civ))
        pending = self.count_expanding_ships()
        return current + pending

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
        if not self.scene.get_civ_planets(self.civ):
            return        
        self._last_time = self.time
        self.time += dt
        duration = 1
        if self.duration_edge(duration):
            self.build_order.update(self, duration * self.build_order_acceleration)
            if self.build_order.is_over():
                self.update_post_build_order(duration * self.build_order_acceleration)
            else: # If build order still going but we have too many upgrades
                if len(self.civ.upgrades_stocked) > 1:
                    self.research_randomly()
            self.update_reactions(duration)

    def get_target_num_planets(self, time):
        return min(int(time / 70 + 2), self.get_max_planets())

    def get_next_attack_countdown(self):
        return 90

    def update_post_build_order(self, dt):
        # Expand or attack if we are behind the expanding curve
        neutral_planets = self.scene.get_civ_planets(None)
        my_planets = self.scene.get_civ_planets(self.civ)
        num = len(my_planets)
        orders = self.get_ordered_ships(self.get_colonist())
        if orders:
            num += len(set([o[1] for o in orders]))

        target_num = self.get_target_num_planets(self.time * self.build_order_acceleration)
        if num < target_num:
            if self.time_behind_expand_curve < 20:
                self.time_behind_expand_curve += dt
            else:
                if neutral_planets:            
                    self.execute_expand(buildorder.BOExpand.TARGET_TYPE_NEAR_HOME)
                    self.time_behind_expand_curve = 0
                else:
                    self.attack_behind_expansion_curve_countdown -= dt
                    if self.attack_behind_expansion_curve_countdown < 0:
                        self.time_behind_expand_curve = 0
                        print("attack because expand curve")
                        self.execute_attack(buildorder.BOAttack.ATTACK_TYPE_OUTLYING)
                        self.attack_behind_expansion_curve_countdown = 120 / self.build_order_acceleration

        # Attack if we're close to winning
        if self.count_attacking_ships() < max(self.get_max_attackers() - 2,3):
            winning_acceleration = 1
            if self.near_winning:
                winning_acceleration = 2

            # only count down when there's no attackers
            self.attack_countdown -= dt * winning_acceleration
            if self.attack_countdown < 0:
                print("attack because attack countdown")
                self.execute_attack(buildorder.BOAttack.ATTACK_TYPE_CENTRAL)
                self.attack_countdown = self.get_next_attack_countdown()

        # Research randomly
        self.research_randomly()

    def research_randomly(self):
        if self.civ.upgrades_stocked:
            rt = self.civ.upgrades_stocked.pop(0)
            available_upgrades = [
                uc for uc in UPGRADE_CLASSES.values()
                if uc.alien_name == self.name
                and uc.resource_type == rt
                and self.difficulty >= uc.alien_min_level
            ]
            if available_upgrades:
                up = random.choice(available_upgrades)
                available_targets = [
                    p for p in self.scene.get_civ_planets(self.civ)
                    if p.is_buildable()
                ]            
                if available_targets:
                    if up.category == "tech":
                        self.research_with_target(up.name, self.civ)
                    else:
                        self.research_with_target(up.name, random.choice(available_targets))        

    def defend_planet(self, planet, total_ships_ratio=None):
        num_ships_to_send = 0
        if total_ships_ratio is not None:
            # Send a number of ships based on the total that we control. 
            # Send a minimum of 1.
            num_ships_to_send = max(total_ships_ratio * len(self.civ.get_all_combat_ships()), 1)
        else:
            num_ships_to_send = 1

        # num_ships_to_send is the total number of ships that we need to send to defend
        # the target planet. Order all the potential sources (our planets with ships)
        # and then iterate through them, sending ships until we hit 0 that we need to send

        all_potential_sources = self.scene.get_civ_planets(self.civ)
        if planet in all_potential_sources:
            all_potential_sources.remove(planet)
        all_potential_sources = [
            s for s in all_potential_sources
            if sum(
                {k:v for k,v in s.ships.items() if k in self.get_attacking_ships()}
            .values()) > 0
        ]
        all_potential_sources.sort(key=lambda p:(p.pos - planet.pos).length_squared())
        if not all_potential_sources:
            return

        for source in all_potential_sources:
            ships = self.get_planet_ship_instances(source)
            ships = [s for s in ships if s in self.get_attacking_ships()]
            num_to_send_from_source = int(min(num_ships_to_send, len(ships)))

            for s in ships[0:num_to_send_from_source]:
                source.emit_ship(s, {'to':planet})
            num_ships_to_send -= num_to_send_from_source
            if num_ships_to_send <= 0:
                break


    def get_defend_countdown(self):
        if self.time == 0:
            return 10
        return 120 - self.difficulty * 10

    def get_defendable_objects(self):
        return self.scene.get_civ_planets(self.civ)

    def update_reactions(self, dt):
        # React to incoming enemies
        my_planets = self.scene.get_civ_planets(self.civ)
        defendables = self.get_defendable_objects()
        self.defend_countdown -= dt
        if self.defend_countdown < 0:
            for ship in self.scene.get_civ_ships(self.scene.player_civ):
                if ship.chosen_target in defendables:
                    p = ship.chosen_target
                    defend_ship_ratio = 0.25
                    if isinstance(p, bossmothership.BossMothership):
                        defend_ship_ratio = 0.5
                    if not isinstance(p, planet.planet.Planet) or (sum(p.ships.values()) < 3):
                        if self.count_attacking_ships(target=ship.chosen_target) == 0:
                            self.defend_planet(ship.chosen_target, defend_ship_ratio)
                            self.defend_countdown = self.get_defend_countdown()
                            break # Only one defend per cycle

        # React to being near winning
        if len(my_planets) > len(self.scene.get_civ_planets(self.scene.player_civ)) + 1:
            self.near_winning = True
        else:
            self.near_winning = False

        # Recall waiting ships
        #if self.duration_edge(20):
        for fleet in self.scene.fleet_managers['enemy'].current_fleets:
            if fleet.is_waiting():
                self.scene.fleet_managers['enemy'].recall_fleet(fleet)            

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

    def get_attacking_ships(self):
        return []

    def get_max_attackers(self):
        curve = {
            1: 0,
            2: 3,
            3: 5,
            4: 6,
            5: 7,
            6: 7,
        }.get(self.difficulty, 999)        

        if self.difficulty > 1 and self.time > 360:
            curve *= 2

        return curve

    def get_build_order_acceleration(self):
        # curve = {
        #     1:0.75, 2:0.85, 3:1.0, 4:1.1,
        #     5:1.2, 6:1.35, 7:1.5, 8:1.65,
        #     9:1.8
        # }
        curve = {
            1:0.85, 2:0.95, 3:1.1, 4:1.25,
            5:1.35, 6:1.55, 7:1.8, 8:2.0,
            9:2.0
        }        
        
        return curve[self.difficulty]

    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.civ.base_stats['planet_health_mul'] = -0.6 + (difficulty - 1) / 6
        self.civ.base_stats['mining_rate'] = 0.65 + 0.1 * difficulty
        self.civ.base_stats['max_ships_per_planet'] = int((difficulty + 5) / 2)
        extra_planets = 0
        if difficulty == 3: extra_planets = 2
        if difficulty == 4: extra_planets = 2
        if difficulty == 5: extra_planets = 2
        if difficulty == 6: extra_planets = 2
        if difficulty == 7: extra_planets = 3
        if difficulty == 8: extra_planets = 3
        if difficulty == 9: extra_planets = 4

        self.build_order_acceleration = self.get_build_order_acceleration()
        extra_pops = difficulty // 2
        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.population += extra_pops
        if difficulty >= 6:
            my_planet.resources.iron = 70
            my_planet.resources.gas = 30
            my_planet.regenerate_art()

        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - my_planet.pos).length_squared())
        near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:extra_planets]
        time_looped = False
        for i in range(extra_planets):
            if difficulty in [6,7,8] and not time_looped:
                near_unclaimed[i].set_time_loop()
                time_looped = True               
            near_unclaimed[i].change_owner(self.civ)
            near_unclaimed[i].population = extra_pops
            near_unclaimed[i].set_health(near_unclaimed[i].get_max_health(), False)

        for planet in self.scene.get_civ_planets(self.civ):
            planet.set_health(planet.get_max_health(), False)            

        self.civ.max_buildings = {
            1:3,
            2:3,
            3:5,
            4:8,5:8,6:8,7:8,8:8,9:8
        }[difficulty]

        self.civ.earn_resource("iron", 150)
        self.civ.earn_resource("ice", 150)
        self.civ.earn_resource("gas", 150)

        self.build_order = buildorder.BuildOrder(self.get_build_order_steps())

    def _get_possible_attack_targets(self, planet):
        near_planets = self.scene.get_planets()
        near_planets.sort(key=lambda x:(x.pos - planet.pos).length_squared())
        near_enemy = [p for p in near_planets if p.owning_civ and p.owning_civ != self.civ][0:2] # 2 nearest    
        
        return near_enemy    

    def count_attacking_ships(self, target=None):
        c = 0
        for ship in self.scene.get_civ_ships(self.civ):
            if not ship.chosen_target:
                continue
            valid_target = ship.chosen_target.owning_civ == self.scene.player_civ
            if target is not None:
                valid_target = ship.chosen_target == target
            if (ship.SHIP_BONUS_NAME != "colonist" and valid_target):
                c += 1
        for planet in self.scene.get_civ_planets(self.civ):
            for ship_type, emit_data in planet.emit_ships_queue:
                valid_target = emit_data['to'].owning_civ and emit_data['to'].owning_civ != self.civ
                if target is not None:
                    valid_target = emit_data['to'] == target
                if ship_type in self.get_attacking_ships() and valid_target:
                    c += 1
        return c

    def count_expanding_ships(self):
        colonists_out = 0
        for ship in self.scene.get_civ_ships(self.civ):
            if ship.SHIP_BONUS_NAME == "colonist":
                colonists_out += 1
        return colonists_out        
                
    def get_colonist(self):
        return ""

    def render(self, screen):
        pass

    def get_max_planets(self):
        return {
            1:3,
            2:4,
            3:5,
            4:999,
            5:999,
            6:999,
            7:999,
            8:999,
            9:999
        }[self.difficulty]
