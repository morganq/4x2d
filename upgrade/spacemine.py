import bullet
import ships
import spaceobject
from helper import clamp


class SpaceMine(spaceobject.SpaceObject):
    def __init__(self, scene, pos, owning_civ, delay=0):
        super().__init__(scene, pos)
        self.owning_civ = owning_civ
        self.set_sprite_sheet("assets/mine.png", 13)
        self.time = -delay
        self.collidable = True
        self.collision_radius = 4
        self.stationary = True
        self.solid = False

    def update(self, dt):
        self.time += dt
        self.frame = int(clamp(self.time * 8, 0, 8))
        if self.time > 1.0:
            self.frame = 8 + int(self.time * 2) % 2
        return super().update(dt)

    def collide(self, other):
        if self.time > 1 and isinstance(other, ships.ship.Ship) and other.owning_civ != self.owning_civ:
            self.time = -10
            b = bullet.Bullet(other.pos, other, self, mods={'damage_base':10, 'blast_radius':10})
            self.scene.game_group.add(b)
        return super().collide(other)
