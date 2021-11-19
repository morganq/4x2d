import pygame
import text
from colors import *
from resources import resource_path
from spritebase import SpriteBase
from v2 import V2


class ShipCounter(SpriteBase):
    def __init__(self, planet):
        super().__init__(V2(0,0))
        self.planet = planet
        self._num_ships = 0
        
        self.visible = False
        self.pos = planet.pos + V2(3,3)
        self.time = 0
        self.ship_img = pygame.image.load(resource_path("assets/i-fighter.png")).convert_alpha()
        self.hourglass_frames = pygame.image.load(resource_path("assets/hourglass.png")).convert_alpha()
        self._generate_image()

    def _generate_image(self):
        r = 8
        w = r*2 + 8
        h = r*2
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PICO_PURPLE, (5,6),5, 0)
        pygame.draw.circle(self.image, PICO_PURPLE, (3 + r,r),r, 0)
        if self.planet.production:
            pygame.draw.circle(self.image, PICO_PURPLE, (9 + r,r),r, 0)
            pygame.draw.rect(self.image, PICO_PURPLE, (3 + r,0,6,r * 2), 0)
        img = self.ship_img
        self.image.blit(img, (-2, 0))
        s = str(int(self._num_ships))            
        tr = text.FONTS['small'].get_rect(s)
        color = PICO_GREEN
        if sum(self.planet.ships.values()) > self.planet.get_max_ships():
            color = PICO_RED
        text_pos = (r - tr[2]/2 + 4, r - tr[3]/2)
        text.FONTS['small'].render_to(self.image, text_pos, s, color)

        if self.planet.production:
            frame = int((self.time * 6) % 11)
            self.image.blit(self.hourglass_frames, (text_pos[0] + 5, text_pos[1] - 1), (frame * 9, 0, 9, 9))

        self._width = w
        self._height = h
        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        in_comm_range = any([civ.in_comm_circle(self.planet.pos) for civ in self.planet.scene.get_enemy_civs(self.planet.owning_civ)])
        if self.planet.owning_civ is None or not self.planet.owning_civ.is_player and not in_comm_range:
            self.visible = False
            return
        self.visible = True
        ships = sum(self.planet.ships.values())
        self._num_ships = ships
        self._generate_image()
        if self._num_ships == 0 and not self.planet.production and not self.planet.owning_civ.is_enemy:
            self.visible = False
        else:
            self.visible = True
        return super().update(dt)
