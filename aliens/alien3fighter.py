from ships.all_ships import register_ship
from ships.fighter import Fighter


@register_ship
class Alien3Fighter(Fighter):
    SHIP_NAME = "alien3fighter"
    DISPLAY_NAME = "Void Fighter"
    FUEL = 9999
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3fighter.png", 12)
