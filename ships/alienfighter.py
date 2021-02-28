from .fighter import Fighter

class AlienFighter(Fighter):
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self._change_image("assets/alien-fighter.png", 12)
        self.name = "alien-fighter"