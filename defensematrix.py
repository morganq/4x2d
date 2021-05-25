from pygame import time
from spaceobject import SpaceObject
from helper import all_nearby
import ships
from bullet import Bullet

class DefenseMatrix(SpaceObject):
    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos)
        self.owning_civ = owning_civ
        self.set_sprite_sheet("assets/defensivematrix.png", 31)
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer > 1:
            for obj in all_nearby(self.pos, self.scene.get_objects_in_range(self.pos, 17), 17):
                if isinstance(obj, ships.ship.Ship):
                    if obj.owning_civ != self.owning_civ:
                        b = Bullet(obj.pos, obj, self, mods={'damage_base':obj.get_max_health() / 10})
                        self.scene.game_group.add(b)
            self.timer = 0

        self.frame = int((self.timer * 4) % 4)

        return super().update(dt)