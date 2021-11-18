from ships.all_ships import register_ship
from ships.fighter import Fighter


@register_ship
class Alien2Fighter(Fighter):
    SHIP_NAME = "alien2fighter"
    BASE_HEALTH = 25
    BASE_DAMAGE = 3
    MAX_SPEED = 5
    DISPLAY_NAME = "Network Fighter"
    FUEL = 9999
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2fighter.png", 13)
    