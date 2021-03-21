from v2 import V2
import game
from spaceobject import SpaceObject
from planet import planet
from helper import get_nearest
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


GRID_SIZE_PIXELS = 10
EXTRA = 20

# TODO: Optimize grid creation. (profile?) Can be done a lot quicker, rather than going cell by cell.


class Pathfinder:
    def __init__(self, scene):
        self.scene = scene
        self._grid = None

    def generate_grid(self, exclude = None):
        exclude = exclude or []
        objects = self.scene.get_objects()
        for obj in exclude:
            objects.remove(obj)

        w = game.RES[0] // GRID_SIZE_PIXELS
        h = game.RES[1] // GRID_SIZE_PIXELS
        grid = []
        for y in range(h):
            grid.append([])
            for x in range(w):
                cell = 1
                center = V2(x * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2, y * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2)
                closest, dist = get_nearest(center, objects)
                if closest:
                    if (dist - closest.radius ** 2 - EXTRA ** 2) < (GRID_SIZE_PIXELS / 2) ** 2:
                        cell = 2
                grid[-1].append(cell)

        self._grid = Grid(matrix=grid)
        #print(Grid(matrix=grid).grid_str())
        return grid

    def find_path(self, a, b):
        if isinstance(a, SpaceObject):
            a = a.pos

        if isinstance(b, SpaceObject):
            b = b.pos         

        grid = self._grid
        start = grid.node(*(a / GRID_SIZE_PIXELS).tuple_int())
        end = grid.node(*(b / GRID_SIZE_PIXELS).tuple_int())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        path = [(V2(*p) + V2(0.5, 0.5)) * GRID_SIZE_PIXELS for p in path]
        #print(grid.grid_str(path=path, start=start, end=end))
        self._grid.cleanup()
        return path