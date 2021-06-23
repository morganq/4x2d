from ships.colonist import Colonist
import random

class Alien1Colonist(Colonist):
    SHIP_BONUS_NAME = 'colonist'
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-colonist.png", 12)
        self.SHIP_NAME = "alien1colonist"

    def colonized(self, planet):
        if planet.resources.iron > 30:
            planet.resources.iron -= 30
            if random.random() > 0.33:
                planet.resources.ice += 20
                planet.resources.gas += 10
            else:
                planet.resources.ice += 10
                planet.resources.gas += 20                
            planet.regenerate_art()
        return super().colonized(planet)