from helper import get_nearest
from aliens.alien3mixin import Alien3Mixin
from ships.bomber import Bomber

class Alien3Bomber(Bomber, Alien3Mixin):
    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3bomber.png", 13)
        self.SHIP_NAME = "alien3bomber"        

    def get_max_speed(self):
        sp = super().get_max_speed()
        if self.in_void():
            sp *= 2
        return sp

    def get_max_shield(self):
        shield = super().get_max_shield()
        if self.in_void():
            shield += 20
        return shield    

    def near_enemies(self):
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_ships(self.scene.my_civ))
        if dsq < 30 ** 2:
            return True
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_planets(self.scene.my_civ))
        if dsq < 50 ** 2:
            return True            
        return False

    def update(self, dt):
        if self.in_void() and not self.near_enemies():
            self.visible = False
        else:
            self.visible = True
        return super().update(dt)