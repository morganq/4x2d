from .fighter import Fighter

class AlienFighter(Fighter):
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-fighter.png", 12)
        self.name = "alien-fighter"