import math
import random

import pygame

import game
import spritebase
from colors import *
from helper import clamp, get_nearest
from resources import resource_path
from v2 import V2


class CloudBackground(spritebase.SpriteBase):
    def __init__(self, pos):
        super().__init__(pos)
        self.blobs = []
        self.time = 0
        self.update_timer = 0
        self.next_blob_timer = 0
        self.mask = pygame.image.load(resource_path("assets/cloudmask.png")).convert_alpha()
        for i in range(200):
            self.step(0.5)

    def add_blob(self):
        blob = {'pos':V2(0,0), 'vel':V2(0,0), 'size':random.random() * 16 + 2, 'seed':random.random(), 'color':PICO_DARKBLUE}
        if random.random() < 0.1:
            blob['color'] = PICO_DARKGRAY
        corner = random.randint(0,3)
        if corner == 0:
            blob['pos'] = V2(0, 0)
            if random.random() < 0.5:
                blob['vel'] = V2(random.random() * 4 + 5, random.random() * 2 - 1)
            else:
                blob['vel'] = V2(random.random() * 2 - 1, random.random() * 4 + 5)
        elif corner == 1:
            blob['pos'] = V2(game.RES[0], 0)
            if random.random() < 0.5:
                blob['vel'] = V2(random.random() * -4 + -5, random.random() * 2 - 1)
            else:
                blob['vel'] = V2(random.random() * 2 - 1, random.random() * 4 + 5)
        elif corner == 2:
            blob['pos'] = V2(game.RES[0], game.RES[1])
            if random.random() < 0.5:
                blob['vel'] = V2(random.random() * -4 + -5, random.random() * 2 - 1)
            else:
                blob['vel'] = V2(random.random() * 2 - 1, random.random() * -4 + -5)
        elif corner == 3:
            blob['pos'] = V2(0, game.RES[1])
            if random.random() < 0.5:
                blob['vel'] = V2(random.random() * 4 + 5, random.random() * 2 - 1)
            else:
                blob['vel'] = V2(random.random() * 2 - 1, random.random() * -4 + -5)

        blob['vel'] *= 1
        self.blobs.append(blob)

    def update(self, dt):
        self.update_timer += dt
        #self.step(dt)        
        #if self.update_timer > 0.2:
        #    self.update_timer = 0
        #    self.generate_image()
        super().update(dt)

    def step(self, dt):
        self.time += dt

        self.next_blob_timer -= dt
        while self.next_blob_timer < 0:
            self.add_blob()
            self.next_blob_timer += 0.35

        for blob in self.blobs:
            blob['pos'] += blob['vel'] * dt
            #blob['size'] = max(blob['size'] - 0.2 * dt, 3)
        
        self.blobs = [b for b in self.blobs if (b['pos'] - V2(*game.RES) / 2).sqr_magnitude() < 400 ** 2]
            
    def generate_image(self):
        self.image = pygame.Surface(game.RES, pygame.SRCALPHA)
        self.image.fill(PICO_BLACK)
        for blob in self.blobs:
            rad = blob['size']# * (math.sin(self.time * blob['seed'] + blob['seed'] * 6.2818) * 0.25 + 1)
            pygame.draw.circle(self.image, blob['color'], blob['pos'].tuple(), int(rad), 0)
        self.image.blit(self.mask, (0,0), None, pygame.BLEND_RGBA_MULT)
