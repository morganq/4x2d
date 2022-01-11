import json
import math
import random

import pygame

import game
import helper
from colors import *
from helper import clamp, rect_contain
from resources import resource_path
from spritebase import SpriteBase

V2 = pygame.math.Vector2

FIELD_SIZE = 80
ACCEL = 200
MOTION_VEC_RADIUS = 5
MAX_PARTICLE_SPEED = 20
BAND_MIN_DISTANCE = 5

GOOD_COLOR_SCHEMES = [
    ((126, 37, 83), (255, 163, 0), PICO_PINK, (255, 236, 39)),
    ((255, 236, 39), (255, 204, 170), (29, 43, 83), (255, 163, 0)),
    ((255, 241, 232), (29, 43, 83), (255, 236, 39), (131, 118, 156)),
    ((255, 204, 170), (0, 135, 81), (29, 43, 83), (255, 241, 232)),
    ((171, 82, 54), (0, 135, 81), (255, 119, 168), (29, 43, 83)),
    ((131, 118, 156), (255, 241, 232), (171, 82, 54), (41, 173, 255)),
    ((126, 37, 83), (255, 236, 39), (255, 241, 232), (255, 163, 0)),
    ((131, 118, 156), (194, 195, 199), (41, 173, 255), (255, 119, 168)),    
    ((131, 118, 156), (0, 135, 81), (0, 0, 0), (194, 195, 199)),
    ((131, 118, 156), (171, 82, 54), (255, 241, 232), (41, 173, 255)),
    ((255, 241, 232), (255, 163, 0), (171, 82, 54), (95, 87, 79)),
    ((41, 173, 255), (95, 87, 79), (255, 241, 232), (255, 119, 168)),    
    ((255, 163, 0), (95, 87, 79), (0, 135, 81), (126, 37, 83)),
    ((131, 118, 156), (171, 82, 54), (255, 204, 170), (126, 37, 83)),
    ((255, 0, 77), (255, 241, 232), (255, 119, 168), (41, 173, 255)),   
]

# Generate a jupiter-like planet by drawing bands of horizontal colors, modified by a flow field.
# Should generate things that look like this:
# https://backyardstargazers.com/wp-content/uploads/2021/03/Gas-Giant-Sizes.jpg.webp

# A Band is two particles (top edge and bottom edge) and a color.
# MenuBackground will fill the area bounded by the motion of the two particles from left to right
class MBBand:
    def __init__(self, p_top, p_bottom, color, is_split = False):
        self.p_top = p_top
        self.p_bottom = p_bottom
        self.color = color
        self.split_distance = abs(p_top.pos.y - p_bottom.pos.y) * 1.5
        self.is_split = is_split

        # We will record all the top and all the bottom points, so we can fill a polygon
        self.top_points = []
        self.bottom_points = []

        # Extras
        self.curve_freq = random.random() * 2 + 0.5
        self.curve_length = random.random() * 20 + 20

# Particle is just position and velocity
class MBParticle:
    def __init__(self, pos):
        self.pos = pos
        self.vel = V2(0,0)
        self.time = 0

        # A particle is done once it reaches the right edge
        self.done = False

        # Extras
        if random.random() < 0.25:
            self.potential_growth = random.random() + 0.1
        else:
            self.potential_growth = 0
        self.potential_max = random.random() * 300 + 100
        self.potential = 0
        self.falling = False        

class MenuBackground(SpriteBase):
    def __init__(self, pos, is_menu = False):
        super().__init__(pos)
        
        self.is_menu = is_menu
        if is_menu:
            data = json.load(open(resource_path("assets/menu_motion.json")))
            self.motion_field = [[V2(*p) for p in row] for row in data]
        else:
            self._generate_motion_field()

        self._generate_image(PICO_WHITE, 150)
        self.wobble_image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        self.time = 0
        self.bands = []
        self.wobble_lines = []
        self.band_images = []
        self.generate()

    def _draw_mask(self,surf=None):
        surf = surf or self.image
        mask = pygame.Surface(game.tuple(Game.inst.game_resolution), pygame.SRCALPHA)
        mask.fill((*PICO_BLACK,0))
        pygame.draw.circle(mask, (255,255,255,255), self.planet_center, self.planet_radius, 0)
        surf.blit(mask, (0,0), None, pygame.BLEND_RGBA_MULT)        

    def field_to_screen(self, pos):
        return (pos * (1/FIELD_SIZE) - V2(0.5,0.5)) * self.planet_radius * 2 + self.planet_center

    def screen_to_field(self, pos):
        p = pos - (self.planet_center - V2(self.planet_radius, self.planet_radius))
        p = p * (FIELD_SIZE / (self.planet_radius * 2))
        return V2(int(clamp(p.x, 0, FIELD_SIZE - 1)), int(clamp(p.y, 0, FIELD_SIZE - 1)))

    def screen_to_field_float(self, pos):
        p = pos - (self.planet_center - V2(self.planet_radius, self.planet_radius))
        return p * (FIELD_SIZE / (self.planet_radius * 2))  

    def _generate_none_field(self):
        f = []
        for i in range(FIELD_SIZE):
            f.append([])
            for j in range(FIELD_SIZE):
                f[-1].append(None)
        return f

    def _generate_motion_field(self):
        self.motion_field = self._generate_none_field()
        for y,row in enumerate(self.motion_field):
            for x,col in enumerate(row):
                self.motion_field[y][x] = V2(1,0)

    def _generate_image(self, background, size):
        w,h = game.tuple(Game.inst.game_resolution)
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        self.image.fill((0,0,0,0))
        planet_center = V2(200,200)
        planet_radius = size
        self.planet_radius = planet_radius
        self.planet_center = planet_center

        pygame.draw.circle(self.image, background, planet_center, planet_radius, 0)
        self._width, self._height = w,h
        self._recalc_rect()

    # Moves the particles in each band
    # Returns True if we're done, False if we're not
    def _update_bands(self, dt):
        any_active = False
        for band in self.bands:
            band_done = band.p_top.done and band.p_bottom.done
            if band_done:
                continue
            # Update each particle
            for p in [band.p_top, band.p_bottom]:
                # If this particle is done, skip it
                if p.done:
                    continue

                any_active = True
                p.time += dt
                vec = self._get_motion_vec(p.pos, MOTION_VEC_RADIUS)

                delta = V2(0,0)
                if p == band.p_top:
                    inwards = V2(0,1)
                    if band.top_points:
                        delta = V2(0,p.pos.y - band.top_points[0].y)
                else:
                    inwards = V2(0,-1)                    
                    if band.bottom_points:
                        delta = V2(0,p.pos.y - band.bottom_points[0].y)                    

                #Wavyness                
                s = math.sin(p.time * band.curve_freq)
                dist = abs(band.p_top.pos.y - band.p_bottom.pos.y)
                # Converge for a little bit
                if dist < 6:
                    p.vel += -inwards * 10 * dt
                elif dist < band.split_distance * 0.7:
                    p.vel += inwards * s * band.curve_length * dt
                else:
                    p.vel += inwards * 200 * dt

                # try to stay straight
                p.vel -= delta * dt * 10

                p.vel += vec * dt * ACCEL

                # Energy thing
                if not p.falling:
                    p.potential += (dist - band.split_distance * 0.5)
                    p.vel += -inwards * max(5000 / (p.potential+1),10) * dt * p.potential_growth
                    if p.potential > p.potential_max:
                        p.falling = True

                if p.falling:
                    p.vel += (inwards + V2(-1,0)) * (p.potential) * dt * p.potential_growth
                    p.potential -= 1000 * dt
                    if p.potential <= 0:
                        p.falling = False

                # Always go right
                eventual_speedup = len(band.top_points) / 20
                p.vel += V2(1,0) * dt * eventual_speedup
                # Cap max speed
                if p.vel.length_squared() > MAX_PARTICLE_SPEED ** 2:
                    p.vel = p.vel.normalize() * MAX_PARTICLE_SPEED
                p.pos += p.vel * dt
                if p.pos.x > self.planet_center.x + self.planet_radius:
                    p.done = True

                # Update the band's shape - add p's position to either top or bottom
                # Will form a polygon
                if p == band.p_top:
                    band.top_points.append(p.pos)
                else:
                    band.bottom_points.append(p.pos)

                if p.time > 30:
                    p.done = True

            # Split the band into two if the vertical distance grows too big
            if not band.is_split:
                if abs(band.p_top.pos.y - band.p_bottom.pos.y) > band.split_distance:
                    band.p_top.done = True
                    band.p_bottom.done = True
                    mid = (band.p_top.pos + band.p_bottom.pos) / 2
                    band.is_split = True
                    pa1 = MBParticle(band.p_top.pos)
                    pa2 = MBParticle(mid)
                    self.bands.append(MBBand(pa1, pa2, band.color, True))
                    pb1 = MBParticle(mid)
                    pb2 = MBParticle(band.p_bottom.pos)
                    self.bands.append(MBBand(pb1, pb2, band.color, True))

        return not any_active

    def generate(self, randomized = True):
        self.bands = []
        self.band_images = []
        self.wobble_lines = []
        if randomized:
            self.rotation = random.random() * 6.2818
        else:
            self.rotation = 0
        def rotate(p):
            d,a = (p - self.planet_center).as_polar()
            a *= 3.14159 / 180
            return helper.from_angle(a + self.rotation) * d + self.planet_center

        if self.is_menu:
            a,b,c,d = random.choice(GOOD_COLOR_SCHEMES)
            print(a,b,c,d)
        else:
            colors = ALL_COLORS[::]
            random.shuffle(colors)
            a,b,c,d = colors[0:4]        

        self.chosen_colors = (a,b,c,d)
        if randomized:
            size = random.randint(70,160)
        else:
            size = 150
        self._generate_image(d, size)
        band_spec = [
            (a, 0.1, 23),
            (b, 0.58, 10),
            (a, 0.5, 23),
            (a, 0.25, 12),
            (a, 0.8, 12),
            (c, 0.66, 12),
            (b, 0.62, 12),
            (b, 0.34, 9),
            (b, 0.9, 15),
        ]
        #band_spec = [(PICO_ORANGE, 0.5, 23),]
        self.bands = []
        for color, yr, h in band_spec:
            h = h * (size / 150)
            yr += random.random() * 0.1 - 0.05
            p1 = MBParticle(self.planet_center + V2(-self.planet_radius, self.planet_radius * (yr - 0.5) * 2 - h))
            p2 = MBParticle(self.planet_center + V2(-self.planet_radius, self.planet_radius * (yr - 0.5) * 2 + h))
            self.bands.append(MBBand(p1,p2,color))
        while not self._update_bands(0.05):
            pass
        for band in self.bands:
            band.top_points = [rotate(p) for p in band.top_points]
            band.bottom_points = [rotate(p) for p in band.bottom_points]
        for band in self.bands:
            img = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
            poly = [tuple(p) for p in band.top_points + band.bottom_points[::-1]]
            pygame.draw.polygon(img, band.color, poly, 1)
            for pts in band.top_points,band.bottom_points:
                wobble_line = pts[::4]
                wobble_line.append(pts[-1])
                self.wobble_lines.append((band.color, wobble_line))
            num = int(clamp(len(band.top_points) / 60, 4, 15))
            for i in range(num):
                mz = min(len(band.top_points), len(band.bottom_points))
                z = int((mz / num) * i)
                fill_pos = (band.top_points[z] + band.bottom_points[z]) / 2
                try:
                    if img.get_at(fill_pos) != band.color:
                        pre_fill = img.copy()
                        self._fill(img, fill_pos, band.color)
                        if img.get_at((0,0)) == band.color:
                            img = pre_fill
                except:
                    pass
            self.image.blit(img, (0,0))
            self.band_images.append(img)
        self._draw_mask()      
        self._shade()

    def _fill(self, surface, position, fill_color):
        fill_color = surface.map_rgb(fill_color)
        position = position
        surf_array = pygame.surfarray.pixels2d(surface)  # Create an array from the surface.
        current_color = surf_array[position[0]][position[1]]  # Get the mapped integer color value.

        # 'frontier' is a list where we put the pixels that's we haven't checked. Imagine that we first check one pixel and 
        # then expand like rings on the water. 'frontier' are the pixels on the edge of the pool of pixels we have checked.
        #
        # During each loop we get the position of a pixel. If that pixel contains the same color as the ones we've checked
        # we paint it with our 'fill_color' and put all its neighbours into the 'frontier' list. If not, we check the next
        # one in our list, until it's empty.

        frontier = [position]
        while len(frontier) > 0:
            x, y = frontier.pop()
            try:  # Add a try-except block in case the position is outside the surface.
                if surf_array[x][y] != current_color:
                    continue
            except IndexError:
                continue
            surf_array[x][y] = fill_color
            # Then we append the neighbours of the pixel in the current position to our 'frontier' list.
            frontier.append((x + 1, y))  # Right.
            frontier.append((x - 1, y))  # Left.
            frontier.append((x, y + 1))  # Down.
            frontier.append((x, y - 1))  # Up.

        pygame.surfarray.blit_array(surface, surf_array)          

    def _get_motion_vec(self,pos,radius):
        out = V2(0,0)
        p1 = self.screen_to_field(pos - V2(radius,radius))
        p2 = self.screen_to_field(pos + V2(radius,radius))
        for x in range(p1.x, p2.x + 1):
            for y in range(p1.y, p2.y + 1):
                v = self.motion_field[y][x]
                if v:
                    out += v.normalize() # instead of here?

        return out.normalize()   

    def motion_draw(self, p1, p2, rad, power, pull):
        delta = p2 - p1
        zero = False
        if delta.x == 0 and delta.y == 0:
            dnorm = delta
            zero = True
        else:
            dnorm = delta.normalize()
        ip1 = rect_contain(p2 - V2(rad,rad), 0,0, FIELD_SIZE-1, FIELD_SIZE-1)
        ip2 = rect_contain(p2 + V2(rad,rad), 0,0, FIELD_SIZE-1, FIELD_SIZE-1)
        for x in range(int(ip1.x), int(ip2.x) + 1):
            for y in range(int(ip1.y), int(ip2.y) + 1):
                pd = V2(x,y) - p2
                towards = -pd.normalize()
                if pd.length_squared() <= rad ** 2:
                    strength = (rad - pd.length()) / rad * power
                    pull_strength = pull * (rad - pd.length()) / rad * power
                    if not zero:
                        self.motion_field[y][x] = self.motion_field[y][x] * (1 - strength) + dnorm * strength
                    self.motion_field[y][x] = self.motion_field[y][x] * (1 - pull_strength) + towards * pull_strength
                    self.motion_field[y][x] = self.motion_field[y][x].normalize()

    def save(self):
        print(self.chosen_colors)
        motion = [[p for p in row] for row in self.motion_field]
        json.dump(motion, open(resource_path("assets/menu_motion.json"), "w"))

    def _shade(self):
        self.shading = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        darken_offset = V2(-0.3, -0.18) * self.planet_radius
        darken_rad = self.planet_radius

        lighten_offset = V2(0.15, 0.07) * self.planet_radius
        lighten_rad = self.planet_radius * 1.13

        for x in range(int(self.planet_center.x) - self.planet_radius,int(self.planet_center.x) + self.planet_radius + 1):
            for y in range(int(self.planet_center.y) - self.planet_radius,int(self.planet_center.y) + self.planet_radius + 1):
                if self.image.get_at((x,y))[3] < 128:
                    continue
                
                delta = V2(x,y) - (self.planet_center + darken_offset)
                if delta.length_squared() > darken_rad ** 2:
                    self.shading.set_at((x,y), (10,0,50,125))

                else:
                    delta = V2(x,y) - (self.planet_center + lighten_offset)
                    if delta.length_squared() > lighten_rad ** 2:
                        self.shading.set_at((x,y), (255,240,150,190))                    

    def update(self, dt):
        self.time += dt
        self.wobble_image = pygame.Surface(self.image.get_size(), pygame.SRCALPHA)
        self.wobble_image.blit(self.image, (0,0))
        z = 0
        rot = helper.from_angle(self.rotation + 3.14159/2)
        for z in range(len(self.band_images)):
            self.wobble_image.blit(self.band_images[z], (0,0))
            for i in range(2):
                color,line = self.wobble_lines[z * 2 + i]
                l2 = [(p + rot * math.sin(i + self.time * (math.sin(z) + 2) / 3) * 1) for i,p in enumerate(line)]
                pygame.draw.lines(self.wobble_image, color, False, l2, 2)
        
        self._draw_mask(self.wobble_image)
        self.wobble_image.blit(self.shading, (0,0))
        return super().update(dt)
