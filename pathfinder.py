from v2 import V2
import game
from planet import planet
from helper import get_nearest
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder


GRID_SIZE_PIXELS = 5
EXTRA = 20

# TODO: Optimize grid creation. (profile?) Can be done a lot quicker, rather than going cell by cell.


class Pathfinder:
    def __init__(self, scene):
        self.scene = scene

    def generate_grid(self, exclude = None):
        exclude = exclude or []
        planets = self.scene.get_planets()
        for planet in exclude:
            planets.remove(planet)

        w = game.RES[0] // GRID_SIZE_PIXELS
        h = game.RES[1] // GRID_SIZE_PIXELS
        grid = []
        for y in range(h):
            grid.append([])
            for x in range(w):
                cell = 1
                center = V2(x * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2, y * GRID_SIZE_PIXELS + GRID_SIZE_PIXELS / 2)
                closest, dist = get_nearest(center, planets)
                if closest:
                    if (dist - closest.radius ** 2 - EXTRA ** 2) < (GRID_SIZE_PIXELS / 2) ** 2:
                        cell = 0
                grid[-1].append(cell)

        return grid

    def find_path(self, a, b):
        exclude = []
        if isinstance(a, planet.Planet):
            exclude.append(a)
            a = a.pos

        if isinstance(b, planet.Planet):
            exclude.append(b)
            b = b.pos         

        matrix = self.generate_grid(exclude)
        grid = Grid(matrix=matrix)
        start = grid.node(*(a / GRID_SIZE_PIXELS).tuple_int())
        end = grid.node(*(b / GRID_SIZE_PIXELS).tuple_int())
        finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
        path, runs = finder.find_path(start, end, grid)
        path = [(V2(*p) + V2(0.5, 0.5)) * GRID_SIZE_PIXELS for p in path]
        #print(grid.grid_str(path=path, start=start, end=end))
        return path