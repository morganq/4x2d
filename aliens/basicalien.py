from aliens.alien import Alien

class BasicAlien(Alien):
    def get_expand_chance(self, planet):    
        num_planets = len(self.scene.get_civ_planets(self.civ))
        if num_planets < 5:
            return 0.2 * planet.population
        else:
            return 0.015 * planet.population