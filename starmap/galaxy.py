import random

import helper
import pygame
import pygame.gfxdraw
from colors import *
from helper import clamp
from resources import resource_path
from spritebase import SpriteBase

V2 = pygame.math.Vector2


def draw_spiral(image, angle, curviness, squash=1, rotate=0):
    w, h = image.get_size()
    cx = w // 2# + random.randint(-1,1)
    cy = h // 2# + random.randint(-1,1)
    pos = V2(cx, cy)
    center = V2(cx, cy)
    radius = w // 2 - 8
    steps = radius
    for i in range(steps):
        t = i / steps
        csize = 2.5 * (1 - t)

        #csize = 1
        rr = int((radius / 8))
        rr2 = int((radius / 14))
        pm, pa = (pos - center).as_polar()
        pa *= 3.14159 / 180
        tp = helper.from_angle(pa + rotate) * pm + center
        tp2 = (helper.from_angle(pa + rotate + 0.05) * pm * 0.95) + center
        brightness = clamp(int(((3 / csize) + 1) * 60 * (1 - t)),0,255)
        tempimage = pygame.Surface((w,h), pygame.SRCALPHA)
        #pygame.gfxdraw.filled_circle(tempimage, int(pos.x), int(pos.y), int(csize), (255,255,255,brightness))
        if csize > 1:
            pygame.draw.circle(tempimage, (255,255,255,brightness), ttuple(p), int(csize))
            pygame.draw.circle(tempimage, (255,255,255,brightness * 0.8), (tp2 + V2(random.randint(-rr2,rr2), random.randint(-rr2,rr2))), int(csize))
        else:
            tempimage.set_at(ttuple(p), (255,255,255, brightness))
            tempimage.set_at((tp2 + V2(random.randint(-rr2,rr2), random.randint(-rr2,rr2))), (255,255,255, brightness))
        tempimage.set_at((tp + V2(random.randint(-rr,rr), random.randint(-rr,rr))), (255,255,255, random.randint(10, 120)))
        if random.random() < 0.25:
            tempimage.set_at((tp + V2(random.randint(-rr,rr), random.randint(-rr,rr))), (255,255,255, random.randint(50, 255)))
        image.blit(tempimage, (0,0))
        off = helper.from_angle(angle) * 1.75
        off = V2(off.x, off.y * squash)
        pos += off
        angle += curviness
        curviness *= 0.93

def palette_map(color, palette):
    avg = int((color[0] + color[1] + color[2]) / 3)
    avg_index = (len(palette) - 1) - int(avg / 255 * (len(palette) - 1))
    return palette[avg_index]

def generate_galaxy_art(radius, also_hover = False):
    w = radius * 2 + 16
    h = w
    image = pygame.Surface((w,h), pygame.SRCALPHA)
    ref_image = pygame.Surface((w,h), pygame.SRCALPHA)
    ref_image.fill(PICO_BLACK)

    squash = random.random() * 0.7 + 0.3
    rotate = random.random() * 6.2818
    num_spirals = max(int(radius / 5.25 * (random.random() * 0.25 + 2.5)),3)
    if num_spirals == 4: # Antifa 
        num_spirals += 1
    curviness = (1.25 / (num_spirals) + 0.05) + random.random()* 0.2 - 0.1
    if random.random() > 0.5:
        curviness = -curviness
    for i in range(num_spirals):
        theta = i / num_spirals * 6.2818
        draw_spiral(ref_image, theta + random.random() * 0.1 - 0.05, curviness, squash, rotate)

    palette = random.choice([
        [PICO_WHITE, PICO_WHITE, PICO_BLUE, PICO_GREYPURPLE, PICO_DARKBLUE],
        [PICO_WHITE, PICO_YELLOW, PICO_ORANGE, PICO_RED, PICO_PURPLE],
        [PICO_WHITE, PICO_YELLOW, PICO_GREEN, PICO_DARKGREEN, PICO_DARKBLUE],
        [PICO_WHITE, PICO_LIGHTGRAY, PICO_GREYPURPLE, PICO_DARKGRAY, PICO_DARKBLUE]
    ])
    
    palette = [PICO_WHITE, random.choice(LIGHTS), random.choice(MEDS), random.choice(DARKS), random.choice(DARKS)]

    if also_hover:
        image2 = pygame.Surface((w,h), pygame.SRCALPHA)

    for x in range(w):
        for y in range(h):
            c1 = ref_image.get_at((x,y))[0:3]
            if c1 != (0,0,0):
                c2 = palette_map(c1, palette)
                image.set_at((x,y), c2)
                if also_hover:
                    palette2 = [palette[0]] + palette[0:-1]
                    image2.set_at((x,y), palette_map(c1, palette2))

    if also_hover:
        return (image, image2)
    return image


class Galaxy(SpriteBase):
    def __init__(self, pos, coords, alien, rewards, difficulty, level, spec, signal, playable):
        super().__init__(pos)
        self.offset = (0.5, 0.5)
        self._generate_image()
        self.coords = coords
        self.alien = alien
        self.rewards = rewards
        self.difficulty = difficulty
        self.level = level
        self.signal = signal
        self.playable = playable
        self.spec = spec
        
        self.selectable = True
        self.selection_radius = self._width // 2
        self.radius = self.selection_radius
        self.is_hover = False
        self.needs_panel_update = False

    def get_selection_info(self):
        return {'type':'galaxy'}
        

    def _generate_image(self):
        self.default_image, self.hover_image = generate_galaxy_art(random.randint(16,25), True)
        self.image = self.default_image
        self._width, self._height = self.default_image.get_size()
        self._recalc_rect()

    def on_mouse_enter(self, pos):
        self.is_hover = True
        self.image = self.hover_image
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self.is_hover = False
        self.image = self.default_image
        return super().on_mouse_exit(pos)
