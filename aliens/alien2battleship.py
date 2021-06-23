from colors import *
from particle import Particle
from ships.battleship import Battleship
from v2 import V2
import random
from ships.all_ships import register_ship

@register_ship
class Alien2Battleship(Battleship):
    HEALTHBAR_SIZE = (24,2)
    SHIP_NAME = "alien2battleship"
    SHIP_BONUS_NAME = 'battleship'

    BASE_HEALTH = 400
    FIRE_RATE = 2.0
    BASE_DAMAGE = 7

    def __init__(self, scene, pos, owning_civ):
        Battleship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2battleship.png", 19)
        self.constructed = True
        self._frame = 2
        self._timers['construction_particle'] = 0

    def update(self, dt):
        if self.constructed:
            return super().update(dt)
        else:
            self._timers['construction_particle'] += dt
            if self._timers['construction_particle'] > 0.4:
                for i in range(3):
                    x = random.randint(0,self.width-1)
                    y = random.randint(0,self.height-1)
                    color = self.image.get_at((x,y))
                    if color[3] > 128 and color[0:3] != PICO_BLACK:
                        p = Particle([PICO_WHITE, PICO_RED, PICO_BROWN], 1, self.pos + V2(x - 9, y - 9), 0.25, V2.random_angle() * 5)
                        self.scene.game_group.add(p)

        if self.health <= 0:
            self.kill()