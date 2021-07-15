import random

import game
import particle
from colors import *
from v2 import V2


class StatusEffect:
    def __init__(self, owner, applier):
        self.applier = applier
        self.owner = owner
        self.name = "default"

    def update(self, dt):
        pass

    def kill(self):
        self.owner.remove_effect(self)

    # Default stacking behavior: Simply add the other effect to the obj
    def stack(self, other_effect):
        self.owner.add_single_effect(other_effect)


class GreyGooEffect(StatusEffect):
    def __init__(self, owner, applier):
        super().__init__(owner, applier)
        self.time = 5
        self.name = "Grey Goo"

    def update(self, dt):
        if not self.owner or not self.owner.alive():
            self.kill()
            return
        self.time -= dt
        if (self.time + dt) % 0.1 < self.time % 0.1:
            pvel = V2.from_angle(random.random() * 6.2818) * 5
            p = particle.Particle([PICO_WHITE, PICO_LIGHTGRAY, PICO_LIGHTGRAY, PICO_DARKGRAY], 1, self.owner.pos - pvel, 0.5 + random.random() * 0.35, pvel)
            p.layer = 3
            game.Game.inst.scene.game_group.add(p)

        if (self.time + dt) % 1 < self.time % 1:
            dmg = (0.25 * len([e for e in self.owner.status_effects if e.name == "Grey Goo"]))
            self.owner.take_damage(dmg, self.applier)
            if self.owner.owning_civ and self.owner.owning_civ.get_stat("grey_goo_collection") > 0:
                self.owner.owning_civ.resources.iron += self.owner.owning_civ.get_stat("grey_goo_collection")
        if self.time <= 0:
            self.kill()
        return super().update(dt)
