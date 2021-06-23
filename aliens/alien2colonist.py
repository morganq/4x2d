from ships.colonist import Colonist
from ships.all_ships import register_ship

@register_ship
class Alien2Colonist(Colonist):
    MAX_SPEED = 5
    BASE_HEALTH = 50
    SHIP_BONUS_NAME = 'colonist'
    SHIP_NAME = "alien2colonist"
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2colonist.png", 13)