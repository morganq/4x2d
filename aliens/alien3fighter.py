from ships.fighter import Fighter

class Alien3Fighter(Fighter):
    SHIP_NAME = "alien3fighter"
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien-fighter.png", 12)
        
    def in_void(self):
        for aura in self.owning_civ.alien.planet_void.values():
            d = (self.pos - aura.pos).sqr_magnitude()
            if d <= aura.radius ** 2:
                return True
        return False

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