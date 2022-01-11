from helper import clamp
import pygame
from resources import resource_path
import pygame
V2 = pygame.math.Vector2
import random
from colors import *

def generate_color_art(radius, angle = None):
    wavy = pygame.image.load(resource_path("assets/planetwavy2.png")).convert_alpha()
    ww, wh = wavy.get_size()
    w = radius * 2
    h = radius * 2

    wavy_angle = angle if angle is not None else random.random() * 6.2818

    def sphere_get(offset, planet_pos):
        spherize = 0.25 + pow(planet_pos.length(), 1.75) / 55.0
        dist,angle = planet_pos.to_polar()
        angle += wavy_angle
        p2 = offset + helper.from_angle(angle) * dist * spherize
        p2.x = clamp(p2.x, 0, ww-1)
        p2.y = clamp(p2.y, 0, wh-1)
        color = wavy.get_at((int(p2.x), int(p2.y)))
        return color

    color_image = pygame.Surface((w,h), pygame.SRCALPHA)
    center = V2(w / 2 - 0.5, h / 2 - 0.5)
    wavy_offset = V2(random.randint(128, 1024 - 128), 128)
    brightness_buckets = [0] * 256
    total_pixels = 0
    for x in range(w):
        for y in range(h):
            planet_pos = (V2(x,y) - center)
            in_circle = planet_pos.length_squared() < (radius - 0.5) ** 2
            if in_circle:
                color = sphere_get(wavy_offset, planet_pos)
                color_image.set_at((x,y), color)
                avg = int(sum(color[0:3]) / 3)
                brightness_buckets[avg] += 1
                total_pixels += 1

    brightness_le = []
    pixels_done = 0
    for i in range(len(brightness_buckets)):
        bb = brightness_buckets[i]
        brightness_le.append((bb + pixels_done) / total_pixels)
        pixels_done += bb
    return color_image, brightness_le    

def palettize(img, brightness1, brightness2, color1, color2):
    w,h = img.get_size()
    out_img = pygame.Surface((w,h), pygame.SRCALPHA)
    for x in range(w):
        for y in range(h):
            inc = img.get_at((x,y))
            if inc[3] > 0:
                avg = int(sum(inc[0:3]) / 3)
                if avg >= brightness1 and avg < brightness2:
                    out_img.set_at((x,y), color2)
                else:
                    out_img.set_at((x,y), color1)

    return out_img

def get_min_max_from_buckets(buckets, rat):
    offset = 0.5 + rat /2 
    minb = None
    maxb = None
    for i in range(len(buckets)):
        if minb == None and buckets[i] >= offset - rat / 2:
            minb = i
        if maxb == None and buckets[i] >= offset + rat / 2:
            maxb = i       
    return (minb, maxb)

def generate_planet_art(radius, white_pct, blue_pct, red_pct, seed=None, angle=None):
    random_state = None
    if seed:
        random_state = random.getstate()
        random.seed(seed)
    white_rat = white_pct / 200 # Even at 100%, it should only take up half the planet's space, so /200.
    blue_rat = blue_pct / 200
    red_rat = red_pct / 200
    angle = angle or random.random() * 6.2818
    img, buckets = generate_color_art(radius, angle = angle)
    minb, maxb = get_min_max_from_buckets(buckets, white_rat)
    out_image = palettize(img, minb, maxb, PICO_GREYPURPLE, PICO_WHITE)

    if blue_pct:
        img, buckets = generate_color_art(radius, angle = angle)
        minb, maxb = get_min_max_from_buckets(buckets, blue_rat)        
        temp_image = palettize(img, minb, maxb, (0,0,0,0), PICO_BLUE)
        out_image.blit(temp_image, (0,0))

    if red_pct:
        img, buckets = generate_color_art(radius, angle = angle)
        minb, maxb = get_min_max_from_buckets(buckets, red_rat)        
        temp_image = palettize(img, minb, maxb, (0,0,0,0), PICO_PINK)
        out_image.blit(temp_image, (0,0))        

    for x in range(radius * 2):
        for y in range(radius * 2):
            d = (V2(x,y) - V2(radius * 0.84, radius * 0.54)).length_squared()
            if d > (radius * 1.0) ** 2:
                c = out_image.get_at((x,y))
                if c[3] > 128:
                    out_image.set_at((x,y), DARKEN_COLOR[c[0:3]])

    if seed:
        random.setstate(random_state)

    return out_image