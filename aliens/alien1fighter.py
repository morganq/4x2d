from ships.fighter import Fighter

class Alien1Fighter(Fighter):
    SHIP_NAME = "alien1fighter"
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-fighter.png", 12)
        