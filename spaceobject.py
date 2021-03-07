from animrotsprite import AnimRotSprite
from healthy import Healthy

class SpaceObject(AnimRotSprite, Healthy):
    HEALTHBAR_SIZE = (20, 3)
    def __init__(self, scene, pos):
        AnimRotSprite.__init__(self, pos)
        self.scene = scene
        self.radius = 1
        self.owning_civ = None
        
        Healthy.__init__(self, scene, meter_size=self.HEALTHBAR_SIZE)