from ships.colonist import Colonist

class Alien3Colonist(Colonist):
    MAX_SPEED = 7
    BASE_HEALTH = 50
    SHIP_BONUS_NAME = 'colonist'
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2colonist.png", 13)
        self.SHIP_NAME = "alien3colonist"
