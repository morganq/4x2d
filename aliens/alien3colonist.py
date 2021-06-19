from aliens.alien3mixin import Alien3Mixin
from ships.colonist import Colonist

class Alien3Colonist(Colonist, Alien3Mixin):
    MAX_SPEED = 7
    BASE_HEALTH = 50
    SHIP_BONUS_NAME = 'colonist'
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3colonist.png", 13)
        self.SHIP_NAME = "alien3colonist"

    def get_max_speed(self):
        sp = super().get_max_speed()
        if self.in_void():
            sp *= 2
        return sp

    def get_max_shield(self):
        shield = super().get_max_shield()
        if self.in_void():
            shield += 20
        return shield