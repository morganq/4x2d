import math
import random

import pygame


def clamp(x, a, b):
    return min(max(x,a),b)

def nearest_order(pos, others):
    return sorted(others, key = lambda x:(x.pos - pos).length_squared())

def nearest_order_pos(pos, others):
    return sorted(others, key = lambda x:(x - pos).length_squared())    

def get_nearest(pos, others):
    dist = 999999999
    res = None
    for other in others:
        delta = (other.get_center() - pos).length_squared()
        if delta < dist:
            dist = delta
            res = other
    return res, dist

def get_nearest_pos(pos, others):
    dist = 999999999
    res = None
    for other in others:
        delta = (other - pos).length_squared()
        if delta < dist:
            dist = delta
            res = other
    return res, dist

def all_nearby(pos, others, range):
    return [o for o in others if (pos - o.pos).length_squared() < range ** 2]

PI = 3.14159
PI2 = 6.2818
def get_angle_delta(a, b):
    a = (a + PI2) % PI2
    b = (b + PI2) % PI2
    result = b - a
    result = (result + PI) % PI2 - PI
    return result

def tuple_int(v2):
    return (int(v2.x), int(v2.y))

def random_angle():
    a = random.random() * 6.2818
    x = math.cos(a)
    y = math.sin(a)
    return pygame.math.Vector2(x,y)

def from_angle(a):
    x = math.cos(a)
    y = math.sin(a)
    return pygame.math.Vector2(x,y)
