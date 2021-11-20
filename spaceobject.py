from collections import defaultdict

from animrotsprite import AnimRotSprite
from healthy import Healthy


class SpaceObject(AnimRotSprite, Healthy):
    HEALTHBAR_SIZE = (20, 3)
    SOID = 0
    def __init__(self, scene, pos):
        AnimRotSprite.__init__(self, pos)
        self.offset = (0.5, 0.5)
        self.scene = scene
        self.status_effects = []
        self.radius = 1
        self.owning_civ = None
        self.debug_id = self.SOID
        self.stationary = True
        SpaceObject.SOID += 1
        Healthy.__init__(self, scene, meter_size=self.HEALTHBAR_SIZE)

    def is_alive(self):
        return self.health > 0 and self.alive()

    def get_stat(self, stat):
        value = 0
        for effect in self.status_effects:
            value += effect.get_stat(stat)
        return value

    def update(self,dt):
        self.update_effects(dt)
        super().update(dt)

    def update_effects(self, dt):
        for effect in self.status_effects:
            effect.update(dt)

    def add_effect(self, effect):
        # Try to stack the effect first of all
        for e in self.status_effects:
            if e.name == effect.name:
                e.stack(effect)
                return

        # Otherwise just add it.
        self.add_single_effect(effect)

    def add_single_effect(self, effect):
        self.status_effects.append(effect)

    def remove_effect(self, effect):
        if effect in self.status_effects:
            self.status_effects.remove(effect)

    def kill(self):
        self.health_bar.kill()
        while(self.status_effects):
            self.status_effects[-1].kill()
        return super().kill()
