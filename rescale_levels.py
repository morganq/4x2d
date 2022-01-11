import json
import os

import pygame
V2 = pygame.math.Vector2

SCALE_FACTOR = (6 / 5, 1)

for fn in os.listdir("levels_500"):
    print(fn)
    level = json.load(open("levels_500/%s" % fn))
    scaled_level = []
    for obj in level:
        if 'pos' in obj:
            p2 = V2(obj['pos'][0] * SCALE_FACTOR[0], obj['pos'][1] * SCALE_FACTOR[1])
            obj2 = {k:v for k,v in obj.items()}
            obj2['pos'] = tuple(p2)
            scaled_level.append(obj2)
    print(level)
    print(scaled_level)
    json.dump(scaled_level, open("levels/%s" % fn, "w"))
