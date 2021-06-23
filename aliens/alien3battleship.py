from colors import *
from particle import Particle
from ships.battleship import Battleship
from v2 import V2
import random

class Alien3Battleship(Battleship):
    HEALTHBAR_SIZE = (24,2)
    SHIP_NAME = "alien3battleship"
    SHIP_BONUS_NAME = 'battleship'

    BASE_HEALTH = 200
    FIRE_RATE = 1.0
    BASE_DAMAGE = 5

    def __init__(self, scene, pos, owning_civ):
        Battleship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3battleship.png", 17)
