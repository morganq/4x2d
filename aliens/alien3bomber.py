from helper import get_nearest
from ships.all_ships import register_ship
from ships.bomber import Bomber


@register_ship
class Alien3Bomber(Bomber):
    SHIP_NAME = "alien3bomber"    
    DISPLAY_NAME = "Void Bomber"
    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3bomber.png", 13)   

    def near_enemies(self):
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_ships(self.scene.player_civ))
        if dsq < 30 ** 2:
            return True
        obj, dsq = get_nearest(self.pos, self.scene.get_civ_planets(self.scene.player_civ))
        if dsq < 50 ** 2:
            return True            
        return False

    def update(self, dt):
        if self.in_void() and not self.near_enemies():
            self.visible = False
        else:
            self.visible = True
        return super().update(dt)

    def emit_thrust_particles(self):
        if self.in_void():
            return
        return super().emit_thrust_particles()
