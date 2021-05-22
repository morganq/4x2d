from aliens.alien import Alien, ALIENS
from helper import clamp

class BasicAlien(Alien):
    name = "basic"

    def set_difficulty(self, difficulty):
        super().set_difficulty(difficulty)
        self.EXPAND_DURATION = max(30 - (difficulty * 2), 10)

        my_planet = self.scene.get_civ_planets(self.civ)[0]
        my_planet.add_ship("alien1warpship")
        my_planet.add_ship("alien1warpship")

    def get_resource_priority_odds(self):
        if self.time < 240:
            return {
                'grow':0.6,
                'produce':0.2,
                'tech':0.2
            }        
        else:
            return {
                'grow':0.33,
                'produce':0.33,
                'tech':0.33
            }             

    def get_attack_chance(self, my_planet, target):
        return sum(my_planet.ships.values()) / 15

    def get_expand_chance(self, planet):    
        num_planets = len(self.scene.get_civ_planets(self.civ))
        z = clamp((120 - self.time) / 40, 1, 3)
        if num_planets < 4:
            return 0.15 * planet.population * z
        else:
            return 0.010 * planet.population

    def get_defend_chance(self, my_planet, target):
        return 0

    def get_attacking_ships(self):
        return ['alien1fighter', 'alien1battleship']

ALIENS['basic'] = BasicAlien