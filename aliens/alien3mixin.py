
class Alien3Mixin:
    def in_void(self):
        for aura in self.owning_civ.alien.planet_void.values():
            d = (self.pos - aura.pos).sqr_magnitude()
            if d <= aura.radius ** 2:
                return True
        return False