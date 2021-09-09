from ships.all_ships import register_ship
from ships.fighter import Fighter


@register_ship
class Alien1Fighter(Fighter):
    SHIP_NAME = "alien1fighter"
    BASE_HEALTH = 7
    BASE_DAMAGE = 3
    FIRE_RATE = 1.25

    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-fighter.png", 12)
        