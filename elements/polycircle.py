import math

import pygame


def draw_polycircle(image, color, pos, radius, width):
    num_points = min(max(int(radius + 12),8),100)
    points = []
    for i in range(num_points):
        theta = i * 6.2818 / num_points
        x = math.cos(theta) * radius + pos[0]
        y = math.sin(theta) * radius + pos[1]
        points.append((int(x), int(y)))

    pygame.draw.polygon(image, color, points, width)
