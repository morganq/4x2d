from .colonist import Colonist

class AlienColonist(Colonist):
    def __init__(self, scene, pos, owning_civ):
        Colonist.__init__(self, scene, pos, owning_civ)
        self._change_image("assets/alien-colonist.png", 12)