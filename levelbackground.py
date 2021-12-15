import math
import random

import pygame

import game
import spritebase
from colors import *
from helper import clamp, get_nearest
from resources import resource_path
from v2 import V2

COLOR_FADE = 0.7

class LevelBackground(spritebase.SpriteBase):
    def __init__(self, pos, size):
        super().__init__(pos)
        self.size = size
        self.twinkle_timer = 0
        #self._generate_image()

    def generate_image(self, objgrid):
        self.image = pygame.Surface(self.size.tuple(), pygame.SRCALPHA)
        self.image.fill((0,0,0,255))
        #dither = pygame.image.load(resource_path("assets/dither.png")).convert_alpha()
        bw = 2
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,0,self.size.x, bw))
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,self.size.y-bw,self.size.x, bw))
        pygame.draw.rect(self.image, PICO_DARKBLUE, (0,0,bw,self.size.y))
        pygame.draw.rect(self.image, PICO_DARKBLUE, (self.size.x-bw,0,bw,self.size.y))
        min_step = 2
        xrange = list(range(min_step, self.image.get_width(), min_step))
        yrange = list(range(min_step, self.image.get_height(), min_step))
        random.shuffle(xrange)
        random.shuffle(yrange)
        for x in xrange:
            for y in yrange:
                if x % (min_step * 4) == 0 and y % (min_step * 4) == 0:
                    self.image.set_at((x,y), PICO_DARKGRAY)                
                density = 0
                for object in objgrid.get_objects_near(V2(x,y), 100):
                    d = (V2(x,y) - object.pos).sqr_magnitude() ** 0.85
                    density += (8000 / max(d,100)) * (object.radius / 6.5)

                density = density ** 0.65 * 1.75
                density_value = 4 - min(int(density / 10),4)
                frequency = min_step * pow(2, density_value + 1)
                f2 = max(frequency / 2, min_step)
                if x % frequency == 0 and y % frequency == 0:
                    self.image.set_at((x,y), PICO_DARKGRAY)

                color = PICO_DARKBLUE
                outside_plus_density = ((V2(x,y) - V2(*game.RES)/2).sqr_magnitude() + density * 20)
                if outside_plus_density > 120 ** 2:
                    val = (math.sqrt(outside_plus_density) - 120) / 50
                    if random.random() < val:
                        color = PICO_PURPLE
                if outside_plus_density > 180 ** 2:
                    color = PICO_PURPLE
                    val = (math.sqrt(outside_plus_density) - 200) / 50
                    if random.random() < val:
                        color = PICO_GREYPURPLE                    

                if random.random() < 0.05:
                    color = PICO_PURPLE
                if random.random() < 0.02:
                    color = PICO_GREYPURPLE
                if random.random() < 0.01:
                    color = PICO_LIGHTGRAY

                if x % frequency == 0 and y % frequency == 0:
                    length_pct = clamp(math.sin(density / 5)*0.65 + 0.75, 0.125, 1.5)
                    length = round(frequency * length_pct / 8)
                    
                    color = tuple([int(c * COLOR_FADE) for c in color])

                    self.image.set_at((x,y), color)
                    hl = frequency / 2
                    if random.random() < 0.65:
                        pygame.draw.line(self.image, color, (x + hl - length,y), (x+ hl + length , y))
                        pygame.draw.line(self.image, color, (x,y + hl - length), (x, y + hl + length))
                        pygame.draw.line(self.image, color, (x - hl - length,y), (x - hl + length , y))
                        pygame.draw.line(self.image, color, (x,y - hl - length), (x, y - hl + length))     

                        if length_pct > 1.35 and random.random() < 0.3:
                            color = tuple([int(c / COLOR_FADE) for c in color])
                            length //= 2
                            pygame.draw.line(self.image, color, (x + hl - length,y), (x+ hl + length , y))
                            pygame.draw.line(self.image, color, (x,y + hl - length), (x, y + hl + length))
                            pygame.draw.line(self.image, color, (x - hl - length,y), (x - hl + length , y))
                            pygame.draw.line(self.image, color, (x,y - hl - length), (x, y - hl + length))
                            self.image.set_at((x,y), color)
                        
        self.base_image = self.image
        #tw = 9
        #th = 7
        #for tx in range(tw):
        #    for ty in range(th):
        #        self.image.blit(dither, (tx * 100, ty * 100))


    # def update(self, dt):
    #     self.twinkle_timer -= dt
    #     if self.twinkle_timer < 0:
    #         self.image = self.base_image.copy()
    #         for i in range(3):
    #             x = random.randint(0, self.size.x / 4) * 4
    #             y = random.randint(0, self.size.x / 4) * 4
    #             self.image.set_at((x,y), PICO_WHITE)
    #         self.twinkle_timer = random.random()
    #     return super().update(dt)
                    
