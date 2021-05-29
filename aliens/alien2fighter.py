from ships.fighter import Fighter

class Alien2Fighter(Fighter):
    SHIP_NAME = "alien2fighter"
    BASE_HEALTH = 30
    BASE_DAMAGE = 3
    MAX_SPEED = 5
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2fighter.png", 13)
    