from colors import PICO_BLUE
from spaceobject import SpaceObject
from helper import all_nearby
import ships
from laserparticle import LaserParticle

class Portal(SpaceObject):
    def __init__(self, scene, pos, other_planet, owning_civ):
        super().__init__(scene, pos)
        self.owning_civ = owning_civ
        self.set_sprite_sheet("assets/portal.png", 9)
        self.other_planet = other_planet
        self.other_portal = None
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer > 1:
            for obj in all_nearby(self.pos, self.scene.get_objects_in_range(self.pos, 20), 20):
                if isinstance(obj, ships.ship.Ship):
                    if obj.owning_civ == self.owning_civ:
                        print(obj.chosen_target)
                        if obj.chosen_target == self.other_planet:
                            lp1 = LaserParticle(obj.pos, self.pos, PICO_BLUE, 0.15)
                            lp2 = LaserParticle(self.pos, self.other_portal.pos, PICO_BLUE, 0.25)
                            delta = obj.pos - self.pos
                            obj.pos = self.other_portal.pos + delta / 2
                            lp3 = LaserParticle(obj.pos, self.other_portal.pos, PICO_BLUE, 0.35)
                            obj.fix_path()
                            self.scene.game_group.add(lp1)
                            self.scene.game_group.add(lp2)
                            self.scene.game_group.add(lp3)
            self.timer = 0
        self.frame = int((self.timer * 2) % 2)
        return super().update(dt)