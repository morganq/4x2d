import random

class Alien:
    EXPAND_DURATION = 10
    ATTACK_DURATION = 20
    COLONIST = 'alien-colonist'

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
    def duration_edge(self, duration):
        if (self.time % duration) < (self._last_time % duration):
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

    def update(self, dt):
        self._last_time = self.time
        self.time += dt
        self.update_resource_priority(dt)
        if self.duration_edge(self.EXPAND_DURATION):
            self.update_expansion()
        if self.duration_edge(self.ATTACK_DURATION):
            self.update_attack()


    def get_expand_chance(self, planet):
        return 0.05 * planet.population

    def get_attack_chance(self, my_planet, target):
        return 0.1

    def update_expansion(self):
        for planet in self.scene.get_civ_planets(self.civ):
            if planet.population <= 1: continue # Don't empty out one of our planets
            # Randomly, decide to expand
            if random.random() < self.get_expand_chance(planet):
                # Find the neutral planets nearest to this planet
                near_planets = self.scene.get_planets()
                near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
                near_unclaimed = [p for p in near_planets if p.owning_civ == None][0:4] # 4 nearest
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
            
            # Find the neutral planets nearest to this planet
            near_planets = self.scene.get_planets()
            near_planets.sort(key=lambda x:(x.pos - planet.pos).sqr_magnitude())
            near_enemy = [p for p in near_planets if p.owning_civ and p.owning_civ != self.civ][0:4] # 4 nearest
            target = random.choice(near_enemy)
            if random.random() < self.get_attack_chance(planet, target):
                pass
        
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
                self.resource_priority = odds[odds.keys()[-1]]
        else:
            self.resource_priority_funs[self.resource_priority](dt)

    def render(self, screen):
        pass