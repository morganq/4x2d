import line
from colors import PICO_LIGHTGRAY, PICO_RED
from helper import get_nearest
from ships.all_ships import register_ship
from ships.fighter import Fighter
from v2 import V2


@register_ship
class Alien1WarpShip(Fighter):
    SHIP_NAME = "alien1warpship"
    SHIP_BONUS_NAME = "fighter"
    FIRE_RATE = 1.0
    BASE_DAMAGE = 4
    FIRE_RANGE = 10
    TETHER_LENGTH = 80
    BASE_HEALTH = 65

    def __init__(self, scene, pos, owning_civ):
        super().__init__(scene, pos, owning_civ)
        self.set_sprite_sheet("assets/warpship.png", 13)
        self.tethered_to, _ = get_nearest(self.pos, self.scene.get_civ_planets(owning_civ))
        self.line1 = line.Line(V2(0,0), V2(0,0), PICO_LIGHTGRAY)
        self.line2 = line.Line(V2(0,0), V2(0,0), PICO_RED)
        self.scene.game_group.add(self.line1)
        self.scene.game_group.add(self.line2)
        self.update_lines()

    def update_lines(self):
        delta = (self.tethered_to.pos - self.pos)
        nd = delta.normalized()
        self.line2.visible = False
        self.line1.pt1 = self.pos + nd * 4
        self.line1.pt2 = self.tethered_to.pos + -nd * (self.tethered_to.radius)
        self.line1.pos = self.line1.pt1
        self.line1._generate_image()     

    def prepare_bullet_mods(self):
        mods = super().prepare_bullet_mods()
        mods['blast_radius'] = 12
        return mods

    def get_stat(self, stat):
        if stat == "warp_drive":
            return 0
        return super().get_stat(stat)

    def update(self, dt):
        self.update_lines()
        if (self.tethered_to.owning_civ != self.owning_civ) or not self.tethered_to.alive():
            self.kill()
            
        if (self.tethered_to.pos - self.pos).sqr_magnitude() > self.TETHER_LENGTH ** 2:
            self.path = None
            self.set_state("returning")
        return super().update(dt)

    def kill(self):
        self.line1.kill()
        self.line2.kill()
        return super().kill()
