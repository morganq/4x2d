import random

import bullet
from colors import PICO_PINK
from planet import planet
from v2 import V2

from ships import fighter
from ships.all_ships import register_ship


@register_ship
class Scout(fighter.Fighter):
    SHIP_NAME = "scout"
    SHIP_BONUS_NAME = "scout"
    BASE_HEALTH = 15
    BASE_DAMAGE = 3
    FIRE_RATE = 0.5
    FIRE_RANGE = 36
    DOGFIGHTS = True
    BOMBS = True
    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self.set_sprite_sheet("assets/scout.png", 12)
        self.busters = 1
        self.buster_time = 1.0
        self.states['siege']['enter'] = self.enter_state_siege
        self.comm_radius = 100
        self.owning_civ.comm_objects.append(self)

    def wants_to_dogfight(self):
        if not isinstance(self.effective_target, planet.Planet):
            return True
        if not self.effective_target.owning_civ or self.effective_target.owning_civ == self.owning_civ:
            return True
        if (self.effective_target.pos - self.pos).sqr_magnitude() > 100 ** 2:
            return True
        if self.busters <= 0:
            return True
        return False

    def enter_state_siege(self):
        self.buster_time = 1.3

    def state_siege(self, dt):
        super().state_siege(dt)
        if self.busters > 0:
            self.buster_time -= dt
            if self.buster_time <= 0:
                self.busters -= 1
                self.buster_time = 0.25
                ang = (self.effective_target.pos - self.pos).to_polar()[1]
                rvel = V2.from_angle(ang + 3.14159 + random.random() - 0.5)
                b = bullet.Bullet(
                    self.pos,
                    self.effective_target,
                    self,
                    vel=rvel,
                    mods={
                        'homing':0.5,
                        'color':PICO_PINK,
                        'missile_speed':-0.65,
                        'life':15,
                        'kill_pop':1,
                        'shape':'circle',
                        'size':2,
                        'trail':PICO_PINK
                    }
                )
                self.scene.game_group.add(b)


