from v2 import V2
import game
from spaceobject import SpaceObject
from planet import planet
from helper import get_nearest
from astar import AStar
from hazard import Hazard
import math
import time

GRID_SIZE_PIXELS = 10
EXTRA = 3

class Pathfinder(AStar):
    def __init__(self, scene):
        self.scene = scene
        self._grid = None
        self.width = 0
        self.height = 0

    def generate_grid(self, exclude = None):
        exclude = exclude or []
        objects = [o for o in self.scene.get_objects_initial() if o.collidable and o.stationary]
        for obj in exclude:
            objects.remove(obj)

        w = game.RES[0] // GRID_SIZE_PIXELS
        h = game.RES[1] // GRID_SIZE_PIXELS
        self.width = w
        self.height = h
        grid = []
        for y in range(h):
            grid.append([])
            for x in range(w):
                cell = 1
                center = V2(x * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2, y * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2)
                closest, dist = get_nearest(center, objects)
                if closest:
                    extra = EXTRA
                    if isinstance(closest, Hazard):
                        extra = 10
                    #if (dist - (closest.radius + extra) ** 2) < (GRID_SIZE_PIXELS / 2) ** 2:
                    if dist < (closest.radius + extra) ** 2:
                        cell = 10
                grid[-1].append(cell)

        #self._grid = Grid(matrix=grid)
        #print(Grid(matrix=grid).grid_str())
        self._grid = grid
        return grid

    def heuristic_cost_estimate(self, n1, n2):
        (x1, y1) = n1
        (x2, y2) = n2
        return abs(x2-x1) + abs(y2-y1)

    def distance_between(self, n1, n2):
        (x1, y1) = n1
        (x2, y2) = n2
        weight = self._grid[y2][x2]# - self._grid[y1][x1]
        off = ((abs(x2 - x1) + abs(y2 - y1) - 1) * 0.414) + 1
        return weight * off

    def neighbors(self, node):
        (x1, y1) = node
        out = []
        for x in range(x1 - 1, x1 + 2):
            for y in range(y1 - 1, y1 + 2):
                if x == x1 and y == y1:
                    continue
                if x >= 0 and x < self.width and y >= 0 and y < self.height:
                    out.append((x,y))
        return out

    def find_path(self, a, b):
        if isinstance(a, SpaceObject):
            a = a.pos

        if isinstance(b, SpaceObject):
            b = b.pos         

        start = (a / GRID_SIZE_PIXELS).tuple_int()
        end = (b / GRID_SIZE_PIXELS).tuple_int()
        t = time.time()
        path = list(self.astar(start, end))
        path = [(V2(*p) + V2(0.5, 0.5)) * GRID_SIZE_PIXELS for p in path]
        if not path:
            return None
        #print("pathfinding", time.time() - t)
        #print(grid.grid_str(path=path, start=start, end=end))
        #self._grid.cleanup()
        return path[3:-3]