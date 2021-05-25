from colors import PICO_LIGHTGRAY
import pygame
from spaceobject import SpaceObject

class Hazard(SpaceObject):
    def __init__(self, scene, pos, size):
        self.size = size
        super().__init__(scene, pos)
        self.collidable = True
        self.stationary = True        
        self.radius = self.get_radius()
        self.collision_radius = self.radius

        self._generate_image()

    def get_radius(self):
        return self.size + 8

    def _generate_image(self):
        r = self.get_radius()
        self._width = r * 2
        self._height = r * 2
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PICO_LIGHTGRAY, (r,r), r, 0)
        self._recalc_rect()