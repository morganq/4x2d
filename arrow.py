import pygame

import game
import sound
import text
from colors import *
from line import ptmax, ptmin
from ships import colonist, fighter
from spritebase import SpriteBase

V2 = pygame.math.Vector2


class Arrow(SpriteBase):
    def __init__(self, pt1, pt2, color):
        super().__init__(pt1)
        self.pt1 = pt1
        self.pt2 = pt2
        self.color = color
        self._generate_image()

    def _generate_image(self):
        thickness = 6
        ht = thickness / 2
        color = self.color
        delta = self.pt2 - self.pt1
        pt1  = V2(self.pt1)
        pt2  = V2(self.pt2)

        w,h = tuple(game.Game.inst.game_resolution)

        forward = delta.normalize()
        side = V2(forward.y, -forward.x)
        points = []
        points.append(pt1 + side * -ht)
        points.append(pt1 + side * ht)
        points.append(pt2 + side * ht + forward * -15)
        points.append(pt2 + side * 15 + forward * -15)
        points.append(pt2)
        points.append(pt2 + side * -15 + forward * -15)
        points.append(pt2 + side * -ht + forward * -15)
        points = [tuple(p) for p in points]

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, points, 0)
        self._width = w
        self._height = h

        self.pos = V2(0,0)
        self._recalc_rect()

class OrderArrow(SpriteBase):
    def __init__(self):
        SpriteBase.__init__(self, V2(0,0))
        self._layer = -1
        self.last_end = None
        sound.play("short3")

    def setup(self, start_planet, end, end_planet=None):
        thickness = 6
        ht = thickness / 2
        color = PICO_LIGHTGRAY
        end_offset = 0
        start_offset = 20
        if end_planet:
            end = end_planet.pos
            color = PICO_WHITE
            end_offset = (end_planet.radius + 6)
        pt1 = start_planet.pos
        pt2 = end
        if not end:
            self.visible = False
            return
        delta = pt2 - pt1

        if delta.length_squared() < 25 ** 2:
            self.visible = False
            return

        self.visible = True

        w,h = tuple(game.Game.inst.game_resolution)

        forward = delta.normalize()
        side = V2(forward.y, -forward.x)
        pt1 += forward * start_offset
        pt2 += forward * -end_offset
        points = []
        points.append(pt1 + side * -ht)
        points.append(pt1 + side * ht)
        points.append(pt2 + side * ht + forward * -15)
        points.append(pt2 + side * 15 + forward * -15)
        points.append(pt2)
        points.append(pt2 + side * -15 + forward * -15)
        points.append(pt2 + side * -ht + forward * -15)
        points = [tuple(p) for p in points]       

        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, color, points, 0)
        self._width = w
        self._height = h

        self.pos = V2(0,0)
        self._recalc_rect()

        if self.last_end is None:
            self.last_end = end

        civ = start_planet.owning_civ
        if civ is not None:
            fighter_range = fighter.Fighter.estimate_flight_range(civ, end_planet) * 0.9
            ranges = {"Fighter Range": fighter_range}
            #if civ.challenge_max_fuel:
            #    ranges["Ship Range"] = colonist.Colonist.estimate_flight_range(civ, end_planet) * 0.9
            title = "Fighter Range"
            if delta.length_squared() > fighter_range ** 2:
                ang = -delta.to_polar()[1] * 180 / 3.14159
                if ang < -90:
                    ang += 180
                    side = -side
                if ang > 90:
                    ang -= 180  
                    side = -side    
                pt2 = pt1 + forward * (fighter_range - start_offset)
                points = []
                ht = thickness / 2
                ht2 = thickness + 3
                mid1 = pt1 + forward * ((fighter_range - start_offset) / 2 - 42)
                mid2 = pt1 + forward * ((fighter_range - start_offset) / 2 + 42)
                pygame.draw.line(self.image, PICO_YELLOW, tuple(pt1 + side * ht), tuple(pt1 + side * ht2), 1)
                pygame.draw.line(self.image, PICO_YELLOW, tuple(pt1 + side * ht2), tuple(mid1 + side * ht2), 1)
                pygame.draw.line(self.image, PICO_YELLOW, tuple(mid2 + side * ht2), tuple(pt2 + side * ht2), 1)
                pygame.draw.line(self.image, PICO_YELLOW, tuple(pt2 + side * ht), tuple(pt2 + side * ht2), 1)
                ts = text.render_multiline(title, "small", PICO_YELLOW)
                ts2 = pygame.transform.rotate(ts, ang)
                center = (pt1 + pt2) / 2 + 6 * side
                self.image.blit(ts2, tuple(center + V2(-ts2.get_width() / 2, -ts2.get_height() / 2)))

                if civ.challenge_max_fuel:
                    ship_range = colonist.Colonist.estimate_flight_range(civ, end_planet) * 0.9
                    if delta.length_squared() > ship_range ** 2:
                        o1s = fighter_range - start_offset
                        o2s = ship_range - start_offset
                        mid3 = pt1 + forward * ((o2s - o1s) / 2 - 22 + o1s)
                        mid4 = pt1 + forward * ((o2s - o1s) / 2 + 22 + o1s)             
                        pt3 = pt1 + forward * (ship_range - start_offset)
                        pygame.draw.line(self.image, PICO_YELLOW, tuple(pt2 + side * ht2), tuple(mid3 + side * ht2), 1)
                        pygame.draw.line(self.image, PICO_YELLOW, tuple(mid4 + side * ht2), tuple(pt3 + side * ht2), 1)
                        pygame.draw.line(self.image, PICO_YELLOW, tuple(pt3 + side * ht), tuple(pt3 + side * ht2), 1)
                        ts = text.render_multiline("Others", "small", PICO_YELLOW)
                        ts2 = pygame.transform.rotate(ts, ang)
                        center = (mid3 + mid4) / 2 + 6 * side
                        self.image.blit(ts2, tuple(center + V2(-ts2.get_width() / 2, -ts2.get_height() / 2)))                    

        if (end - self.last_end).length_squared() > 10 ** 2:
            if end_planet:
                sound.play("short2")
            else:
                sound.play("short1")
            self.last_end = end        
