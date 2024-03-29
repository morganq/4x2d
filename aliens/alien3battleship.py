import random

import pygame
from colors import *
from particle import Particle
from ships.all_ships import register_ship
from ships.battleship import Battleship

V2 = pygame.math.Vector2


@register_ship
class Alien3Battleship(Battleship):
    HEALTHBAR_SIZE = (24,2)
    SHIP_NAME = "alien3battleship"
    SHIP_BONUS_NAME = 'battleship'
    DISPLAY_NAME = "Mothership"

    BASE_HEALTH = 200
    FIRE_RATE = 1.85
    BASE_DAMAGE = 7
    FUEL = 9999

    def __init__(self, scene, pos, owning_civ):
        Battleship.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien3battleship.png", 17)
