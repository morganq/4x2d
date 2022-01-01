from ships.all_ships import register_ship
from ships.colonist import Colonist


@register_ship
class Alien3Colonist(Colonist):
    MAX_SPEED = 7
    BASE_HEALTH = 50
    SHIP_NAME = "alien3colonist"
    SHIP_BONUS_NAME = 'colonist'
    
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3colonist.png", 13)
