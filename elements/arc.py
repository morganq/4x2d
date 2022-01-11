import math

import pygame
import pygame
V2 = pygame.math.Vector2


def make_arc(color, radius, a1, a2, width=1):
    surf = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)
    mask = pygame.Surface((radius*2,radius*2), pygame.SRCALPHA)
    pygame.draw.circle(surf, color, (radius,radius), radius, width)
    max_angle_delta = math.pi / 4
    direction = 1
    if a2 < a1:
        direction = -1
    angle = a1
    poly = [(radius, radius)]
    poly.append((helper.from_angle(angle) * (radius + width + 2) + V2(radius, radius)).tuple_round())
    while angle < a2:
        #p1 = helper.from_angle(angle) * (radius + width + 1)
        angle += min(max_angle_delta, a2 - angle)
        poly.append((helper.from_angle(angle) * (radius + width + 2) + V2(radius, radius)).tuple_round())
        print(angle)
    pygame.draw.polygon(mask, (255,255,255), poly, 0)
    surf.blit(mask, (0,0), None, pygame.BLEND_RGBA_MULT)
    return surf

def draw_arc(surf, color, pos, radius, a1, a2, width=1):
    s2 = make_arc(color, radius, a1, a2, width)
    surf.blit(s2, (pos[0] - radius, pos[1] - radius))
