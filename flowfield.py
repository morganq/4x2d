import time
from math import inf

import asteroid
import game
import hazard
import planet
from helper import clamp, get_nearest
from v2 import V2

GRIDSIZE = 7
EXTRA = 5

class FlowFieldMap:
    def __init__(self) -> None:
        self.fields = {}
        self.gw = int(game.RES[0] / GRIDSIZE)
        self.gh = int(game.RES[1] / GRIDSIZE)        

    def generate(self, scene):
        avoidees = []
        targetables = []
        for obj in scene.get_objects_initial():
            if isinstance(obj, planet.planet.Planet) or isinstance(obj, asteroid.Asteroid):
                avoidees.append(obj)
                targetables.append(obj)
            if isinstance(obj, hazard.Hazard):
                avoidees.append(obj)

        base_grid = self._generate_base_grid(avoidees)

        for obj in targetables:
            self.fields[obj] = FlowField(game.RES, avoidees, obj, base_grid)

    def _generate_base_grid(self, avoidees):
        grid = []
        for gy in range(self.gh):
            grid.append([])
            for gx in range(self.gw):
                cell = None
                center = V2(gx * GRIDSIZE + GRIDSIZE / 2, gy * GRIDSIZE + GRIDSIZE / 2)
                closest, dist = get_nearest(center, avoidees)
                if closest:
                    extra = EXTRA
                    if isinstance(closest, hazard.Hazard):
                        extra = 6
                    if dist < (closest.radius + extra) ** 2:
                        cell = closest
                grid[-1].append(cell)  
        return grid      

    def get_vector(self, pos, target, radius):
        return self.fields[target].get_vector(pos, radius)

    def walk_field(self, pos, target, dist):
        return self.fields[target].walk_field(pos, dist)

    def has_field(self, target):
        return target in self.fields

# From https://howtorts.github.io/2014/01/04/basic-flow-fields.html
class FlowField:
    def __init__(self, size, avoidees, obj, base_grid) -> None:
        self.size = size
        self.base_grid = base_grid
        self.grid = []
        self.gw = int(self.size[0] / GRIDSIZE)
        self.gh = int(self.size[1] / GRIDSIZE)
        self.avoidees = avoidees
        self.obj = obj
        self._generate_field()

    def _get_neighbors(self, x, y):
        n = []   
        if x > 0: n.append((x-1,y))
        if x < self.gw - 1: n.append((x+1,y))
        if y > 0: n.append((x, y-1))
        if y < self.gh - 1: n.append((x, y+1))
        return n

    def _get_8_neighbors(self, x, y):
        n = []      
        for ix in range(x-1, x+2):
            for iy in range(y-1,y+2):
                if ix == x and iy == y: 
                    continue
                if (ix > 0 and ix < self.gw - 1 and iy > 0 and iy < self.gh - 1):
                    n.append((ix,iy))
        return n

    def _generate_dijkstra_grid(self):
        grid = []

        # Generate Nones for unvisited, inf for obstacles
        for gy in range(self.gh):
            grid.append([])
            for gx in range(self.gw):
                cell = self.base_grid[gy][gx]
                if cell == self.obj:
                    cell = None
                elif cell:
                    cell = inf
                grid[-1].append(cell)

        end = (self.obj.pos / GRIDSIZE).tuple_int()
        to_visit = [end]
        grid[end[1]][end[0]] = 0

        while to_visit:
            current = to_visit.pop(0)
            current_distance = grid[current[1]][current[0]]
            neighbors = self._get_neighbors(*current)

            for n in neighbors:
                if grid[n[1]][n[0]] is None:
                    grid[n[1]][n[0]] = current_distance + 1
                    to_visit.append(n)

        return grid
        

    def _generate_field(self):
        
        self.grid = []
        for gy in range(self.gh):
            self.grid.append([])
            for gx in range(self.gw):
                self.grid[-1].append(None)

        dgrid = self._generate_dijkstra_grid()
	
        for x in range(self.gw):
            for y in range(self.gh):
                if dgrid[y][x] == inf:
                    continue
                
                min = None
                min_dist = 0 #??
                for n in self._get_8_neighbors(x,y):
                    nval = dgrid[n[1]][n[0]]
                    if nval is None:
                        nval = inf
                        print("Weird neighbor issue:", n)
                    mval = dgrid[y][x]
                    if mval is None:
                        mval = inf
                        print("Weird neighbor issue:", n)
                    dist = nval - mval
                    if dist < min_dist:
                        min = n
                        min_dist = dist

                    if min is not None:
                        self.grid[y][x] = (V2(*min) - V2(x,y))#.normalized() # maybe do it here?

    def get_vector(self, pos, radius):
        out = V2(0,0)
        x1 = int(clamp((pos.x - radius) / GRIDSIZE, 0, self.gw-1))
        x2 = int(clamp((pos.x + radius) / GRIDSIZE, 0, self.gw-1))
        y1 = int(clamp((pos.y - radius) / GRIDSIZE, 0, self.gh-1))
        y2 = int(clamp((pos.y + radius) / GRIDSIZE, 0, self.gh-1))
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                v = self.grid[y][x]
                if v:
                    out += v.normalized() # instead of here?

        return out.normalized()


    def walk_field(self, pos, distance):
        walked = 0
        p = pos.copy()
        while walked < distance:
            p += self.get_vector(p, 10) * GRIDSIZE
            walked += GRIDSIZE
        return p
