import text
from colors import *
from spritebase import SpriteBase

ORDER = ['fighter', 'scout', 'bomber', 'interceptor', 'battleship', 'other']

class CivShipUI(SpriteBase):
    def __init__(self, pos, civ):
        super().__init__(pos)
        self.civ = civ

    def _generate_image(self):
        ships_str = ""
        for shipdata in self.civ.get_all_combat_ships():
            ships_str += shipdata['name'][0].upper()
        s = text.render_multiline(ships_str, "small", PICO_WHITE, wrap_width=200)
        self.image = s
        self._width, self._height = self.image.get_size()
        self._recalc_rect

    def update(self, dt):
        self._generate_image()
        return super().update(dt)
