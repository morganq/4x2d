from .colonist import Colonist

class AlienColonist(Colonist):
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-colonist.png", 12)