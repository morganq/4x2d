import math
import random

import explosion
import game
import particle
import ships
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
    def stack(self, fresh_effect):
        self.owner.add_single_effect(fresh_effect)

    def get_stat(self, stat):
        return 0


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
            if self.owner.owning_civ == self.applier.owning_civ:
                self.kill()
                return
            dmg = (0.25 * len([e for e in self.owner.status_effects if e.name == "Grey Goo"]))
            self.owner.take_damage(dmg, self.applier)
            if self.owner.owning_civ and self.owner.owning_civ.get_stat("grey_goo_collection") > 0:
                self.owner.owning_civ.resources.iron += self.owner.owning_civ.get_stat("grey_goo_collection")
        if self.time <= 0:
            self.kill()
        return super().update(dt)

class ShipBoostEffect(StatusEffect):
    def __init__(self, owner, applier):
        super().__init__(owner, applier)
        self.stacks = 1
        self.particle_timer = 0

    def stack(self, fresh_effect):
        self.stacks += 1
    
    def get_stat(self, stat):
        return {
            'ship_speed_mul':0.1 * self.stacks,
            'ship_fire_rate':0.05 * self.stacks
        }.get(stat, 0)

    def update(self, dt):
        super().update(dt)
        if not isinstance(self.owner, ships.ship.Ship):
            self.kill()
            return
            
        self.particle_timer += dt
        if self.particle_timer > 0.4:
            pos = self.owner.pos
            def sf(t):
                return math.sin(t * 3.14159)
            e = explosion.Explosion(pos, [PICO_BLUE, PICO_BLUE, PICO_BLUE, PICO_WHITE, PICO_WHITE, PICO_BLUE], 0.8, 3, line_width=1)
            self.owner.scene.game_group.add(e)
            self.particle_timer = 0


