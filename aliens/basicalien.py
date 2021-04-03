from aliens.alien import Alien, ALIENS

class BasicAlien(Alien):
    name = "basic"
    def get_expand_chance(self, planet):    
        num_planets = len(self.scene.get_civ_planets(self.civ))
        if num_planets < 5:
            return 0.1 * planet.population
        else:
            return 0.015 * planet.population

ALIENS['basic'] = BasicAlien