from ships.all_ships import register_ship
from ships.fighter import Fighter

from aliens.alien3mixin import Alien3Mixin


@register_ship
class Alien3Fighter(Fighter, Alien3Mixin):
    SHIP_NAME = "alien3fighter"
    DISPLAY_NAME = "Void Fighter"
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3fighter.png", 12)

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
