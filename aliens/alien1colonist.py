from ships.colonist import Colonist

class Alien1Colonist(Colonist):
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-colonist.png", 12)
        self.SHIP_NAME = "alien1colonist"