import math
import random

import explosion
import game
import particle
import ships
from colors import *
from economy import RESOURCE_COLORS
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
        if (self.time + dt) % 0.25 < self.time % 0.25:
            pvel = V2.from_angle(random.random() * 6.2818) * 5
            p = particle.Particle([PICO_WHITE, PICO_LIGHTGRAY, PICO_LIGHTGRAY, PICO_DARKGRAY], 1, self.owner.pos - pvel, 0.5 + random.random() * 0.35, pvel)
            p.layer = 3
            game.Game.inst.scene.game_group.add(p)

        if (self.time + dt) % 1 < self.time % 1:
            if self.owner.owning_civ == self.applier.owning_civ:
                self.kill()
                return
            dmg = (0.1 * len([e for e in self.owner.status_effects if e.name == "Grey Goo"])) + 0.25
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

class DamageBoostEffect(StatusEffect):
    def __init__(self, owner, applier):
        super().__init__(owner, applier)
        self.name = "damage_boost"

    def get_stat(self, stat):
        return {'ship_weapon_damage':4}.get(stat, 0)


class MultiBonusEffect(StatusEffect):
    def __init__(self, owner, applier, resources):
        super().__init__(owner, applier)
        self.resources = resources
        self.name = "multi_bonus"
        self.time = 999
        self.particle_time = 0

    def update(self, dt):
        self.time += dt
        self.particle_time += dt
        if self.particle_time > 0.1:
            for res in self.resources.data.keys():
                amt = self.resources.data[res]
                if amt > 0:
                    pos = V2.from_angle(self.time * 2) * 6 + self.owner.pos
                    p = particle.Particle([RESOURCE_COLORS[res]], 1, pos, amt / 100, V2.random_angle() * 2)
                    self.owner.scene.game_group.add(p)
            self.particle_time = 0
        return super().update(dt)

    def get_stat(self, stat):
        return {
            'ship_speed_mul': 1.0 * self.resources.iron / 100,
            'ship_fire_rate': 0.5 * self.resources.ice / 100,
            'ship_health_mul': 1.0 * self.resources.gas / 100
        }.get(stat, 0)
