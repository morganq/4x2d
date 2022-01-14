import math
import random

import numba
import numba.types
import numpy as np
import pygame
from pygame.surface import Surface

import game
import spritebase
from colors import *
from helper import clamp, get_nearest
from resources import resource_path

V2 = pygame.math.Vector2


COLOR_FADE = 0.7

@numba.njit
def _get_sq_distance_from_nearest_planet(x, y, planets_arr) -> float:
    closest = 999999999
    for i in range(planets_arr.shape[0]):
        dx = planets_arr[i][0] - x
        dy = planets_arr[i][1] - y
        dsq = dx ** 2 + dy ** 2
        if dsq < closest:
            closest = dsq

    return closest

@numba.njit
# returns between 0 and 1
def _get_density(x, y, planets_arr, r) -> float:
    density = 0.0
    for i in range(planets_arr.shape[0]):
        dx = planets_arr[i][0] - x
        dy = planets_arr[i][1] - y
        dsq = dx ** 2.0 + dy ** 2.0
        if dsq < (r * 2) ** 2.0:
            d = dsq ** 0.90
            density += (r / max(d,r)) * (planets_arr[i][2] / 22.5)
    
    density = density ** 0.75 * 1.75

    return min(density, 1)

@numba.njit
def _create_background(width:int, height:int, planets_arr:np.ndarray, t:float) -> np.ndarray:
    screen_arr = np.zeros((width, height, 3), dtype=np.int32)
    min_step = 2
    centerx = width // 2
    centery = height // 2

    def pixel(x, y, color):
        for i in range(3):
            screen_arr[x, y, i] = int(color[i])

    def hline(x1, x2, y, color):
        for j in range(max(x1,0), min(x2,width-1)):
            pixel(j, y, color)

    def vline(x, y1, y2, color):
        for j in range(max(y1,0), min(y2,height-1)):
            pixel(x, j, color)            

    def pseudorandom(x, y, a):
        return (x * 0.3994 + y * 0.14512 + (t * 0.0025 * math.sin(a)) + ((x+1) / (y+1) * 100 * a) * 5.1237) % 1

    CORES = 2
    for start in numba.prange(CORES):
        for x in range(min_step + start * min_step, width, min_step * CORES):
            for y in range(min_step, height, min_step):
                color = PICO_BLACK
                if x % (min_step * 4) == 0 and y % (min_step * 4) == 0:
                    pixel(x, y, PICO_DARKGRAY)

                density = _get_density(x, y, planets_arr, 100 + math.sin(t / 3) * 20)
                density = density * (1 + math.sin(t / 30) / 4)
                density_value = 4 - min(int(density * 4),4)
                frequency = int(min_step * pow(2, density_value + 1))
                f2 = max(frequency / 2, min_step)
                #if x % frequency == 0 and y % frequency == 0:
                    #pixel(x, y, PICO_BLUE)

                color = PICO_DARKBLUE
                cdx = (centerx - x)
                cdy = (centery - y)
                centerdsq = cdx ** 2 + cdy ** 2
                outside_plus_density = centerdsq + density * 1200
                if outside_plus_density > 120 ** 2:
                    val = (math.sqrt(outside_plus_density) - 120) / 50
                    if pseudorandom(x,y,1) < val:
                        color = PICO_PURPLE
                if outside_plus_density > 180 ** 2:
                    color = PICO_PURPLE
                    val = (math.sqrt(outside_plus_density) - 200) / 50
                    if pseudorandom(x,y,2) < val:
                        color = PICO_GREYPURPLE

                #color = PICO_PURPLE

                if pseudorandom(x, y,3) < 0.05:
                    color = PICO_PURPLE
                if pseudorandom(x, y,4) < 0.02:
                    color = PICO_GREYPURPLE
                if pseudorandom(x, y,5) < 0.01:
                    color = PICO_LIGHTGRAY

                if x % frequency == 0 and y % frequency == 0:
                    length_pct = min(max(math.sin(density * 8)*0.65 + 0.75, 0.125), 1.5)
                    length = round(frequency * length_pct / 8)
                    color = [int(c * COLOR_FADE) for c in color]
                    pixel(x,y,color)
                    hl = frequency / 2.0

                    if pseudorandom(x,y,6) < 0.65:
                        hline(x + hl - length, x + hl + length, y, color)
                        hline(x - hl - length, x - hl + length, y, color)
                        vline(x, y + hl - length, y + hl + length, color)
                        vline(x, y - hl - length, y - hl + length, color)

                        if length_pct > 1.35 and pseudorandom(x,y,7) < 0.3:
                            color = [int(c / COLOR_FADE) for c in color]
                            length //= 2
                            hline(x + hl - length, x + hl + length, y, color)
                            hline(x - hl - length, x - hl + length, y, color)  
                            vline(x, y + hl - length, y + hl + length, color)
                            vline(x, y - hl - length, y - hl + length, color)                             
                            pixel(x,y,color)                     

    return screen_arr

def create_background(width, height, planets, t):
    planets_arr = np.zeros((len(planets),3), dtype=np.int32)
    for i,planet in enumerate(planets):
        planets_arr[i][0] = planet.x
        planets_arr[i][1] = planet.y
        planets_arr[i][2] = planet.radius
    screen_arr = _create_background(int(width), int(height), planets_arr, t)
    return pygame.surfarray.make_surface(screen_arr)


class LevelBackground(spritebase.SpriteBase):
    def __init__(self, pos, size):
        super().__init__(pos)
        self.size = size
        self.twinkle_timer = 0
        self.time = 0
        #self._generate_image()

    def update(self, dt):
        self.time += dt
        #self.image = create_background(*self.size, self.objgrid.get_objects(), self.time)
        return super().update(dt)

    def generate_image(self, objgrid):
        self.objgrid = objgrid
        self.image = create_background(*self.size, objgrid.get_objects(), self.time)

    def _generate_image(self, objgrid):
        self.image = pygame.Surface(self.size, pygame.SRCALPHA)
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
                    d = (V2(x,y) - object.pos).length_squared() ** 0.85
                    density += (8000 / max(d,100)) * (object.radius / 6.5)

                density = density ** 0.65 * 1.75
                density_value = 4 - min(int(density / 10),4)
                frequency = min_step * pow(2, density_value + 1)
                f2 = max(frequency / 2, min_step)
                if x % frequency == 0 and y % frequency == 0:
                    self.image.set_at((x,y), PICO_DARKGRAY)

                color = PICO_DARKBLUE
                outside_plus_density = ((V2(x,y) - V2(*game.RES)/2).length_squared() + density * 20)
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
                    
