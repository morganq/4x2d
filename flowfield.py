import time
from math import inf

import asteroid
import game
import hazard
import planet
from helper import clamp, get_nearest
from v2 import V2

GRIDSIZE = 7
EXTRA = 9

class FlowFieldMap:
    def __init__(self) -> None:
        self.fields = {}
        self.gw = int(game.RES[0] / GRIDSIZE)
        self.gh = int(game.RES[1] / GRIDSIZE)
        self.offset = game.Game.inst.game_offset     
        self._base_grid = None
        self._avoidees = None
        self._field_in_progress = None
        self.boss = None

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
        self._base_grid = base_grid
        self._avoidees = avoidees

        for obj in targetables:
            self.fields[obj] = FlowField(game.RES, self.offset, avoidees, obj, base_grid)

    def _generate_base_grid(self, avoidees):
        grid = []
        for gy in range(self.gh):
            grid.append([])
            for gx in range(self.gw):
                cell = None
                center = V2(gx * GRIDSIZE + GRIDSIZE / 2, gy * GRIDSIZE + GRIDSIZE / 2) + self.offset
                closest, dist = get_nearest(center, avoidees)
                if closest:
                    extra = EXTRA
                    if isinstance(closest, hazard.Hazard):
                        extra = 6
                    if dist < (closest.radius + extra) ** 2:
                        #print(center, closest.pos, closest)
                        delta = (center - closest.pos).normalized()
                        cell = (closest, delta)
                grid[-1].append(cell)  
        return grid      
        

    def get_vector(self, pos, target, radius):
        return self.fields[target].get_vector(pos, radius)

    def walk_field(self, pos, target, dist):
        return self.fields[target].walk_field(pos, dist)

    def has_field(self, target):
        return target in self.fields

    def get_grid_tuple(self, pos):
        cx = int(clamp((pos.x) / GRIDSIZE, 0, self.gw-1))
        cy = int(clamp((pos.y) / GRIDSIZE, 0, self.gh-1))
        return (cx, cy)

    def get_grid_quantized_pos(self, pos):
        cx, cy = self.get_grid_tuple(pos)
        return V2((cx + 0.5) * GRIDSIZE, (cy + 0.5) * GRIDSIZE)

    def update(self, dt):
        if self.boss:
            #print("--")
            if self.boss not in self.fields:
                self.fields[self.boss] = FlowField(game.RES, self.offset, self._avoidees, self.boss, self._base_grid)
                #print("Making complete boss field")
            if self._field_in_progress is None:
                self._field_in_progress = FlowField(game.RES, self.offset, self._avoidees, self.boss, self._base_grid, staged_calculation=True)
                #print("Making staged boss field")
            else:
                if not self._field_in_progress.fully_calculated:
                    #print("Stepping boss field")
                    self._field_in_progress.step_calculation()
                if self._field_in_progress.fully_calculated:
                    #print("Calculation complete")
                    self.fields[self.boss] = self._field_in_progress
                    self._field_in_progress = None



# From https://howtorts.github.io/2014/01/04/basic-flow-fields.html
class FlowField:
    def __init__(self, size, offset, avoidees, obj, base_grid, staged_calculation=False) -> None:
        self.size = size
        self.offset = offset
        self.base_grid = base_grid
        self.dgrid = None
        self.grid = []
        self.gw = int(self.size[0] / GRIDSIZE)
        self.gh = int(self.size[1] / GRIDSIZE)
        self.avoidees = avoidees
        self.obj = obj
        self.fully_calculated = True
        if staged_calculation:
            self.fully_calculated = False
            self._calc_it = self._step_calculation()
        else:
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
                if cell:
                    if cell[0] == self.obj:
                        cell = None
                    else:
                        cell = (9999, cell[1])
                grid[-1].append(cell)

        end = ((self.obj.pos - self.offset) / GRIDSIZE).tuple_int()
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
        
    def step_calculation(self):
        try:
            next(self._calc_it)
        except StopIteration:
            self.fully_calculated = True


    def _step_calculation(self):
        self.grid = []
        for gy in range(self.gh):
            self.grid.append([])
            for gx in range(self.gw):
                self.grid[-1].append(None)
        yield 1

        dgrid = self._generate_dijkstra_grid()
        self.dgrid = dgrid
	
        for x in range(self.gw):
            for y in range(self.gh):
                if dgrid[y][x] == inf:
                    continue
                
                min = None
                min_dist = 999999999
                inf_exception_dir = None
                mval = dgrid[y][x]
                #deltas = []
                for n in self._get_8_neighbors(x,y):
                    nval = dgrid[n[1]][n[0]]
                    if nval is None:
                        nval = 9999
                        #print("Weird neighbor issue: n", n)
                    if mval is None:
                        mval = 9999
                        #print("Weird neighbor issue: m ", (x,y))
                    if isinstance(nval, tuple):
                        nval = nval[0]
                    if isinstance(mval, tuple):
                        inf_exception_dir = mval[1]
                        mval = mval[0]
                    dist = nval - mval
                    #deltas.append((n, (x,y), nval, mval))
                    if dist < min_dist:
                        min = n
                        min_dist = dist

                if inf_exception_dir:
                    self.grid[y][x] = inf_exception_dir
                elif min is not None:
                    self.grid[y][x] = (V2(*min) - V2(x,y))#.normalized() # maybe do it here?
                else:
                    print("no min but also no inf exception", x,y)
                    #print(deltas)
            if x % (self.gw // 64) == 0:
                yield x
        yield 4

    def _generate_field(self):
        for calc in self._step_calculation():
            pass

    def get_vector(self, pos, radius):
        out = V2(0,0)
        pos = pos - self.offset
        cx = int(clamp((pos.x) / GRIDSIZE, 0, self.gw-1))
        cy = int(clamp((pos.y) / GRIDSIZE, 0, self.gh-1))
        x1 = int(clamp((pos.x - radius) / GRIDSIZE, 0, self.gw-1))
        x2 = int(clamp((pos.x + radius) / GRIDSIZE, 0, self.gw-1))
        y1 = int(clamp((pos.y - radius) / GRIDSIZE, 0, self.gh-1))
        y2 = int(clamp((pos.y + radius) / GRIDSIZE, 0, self.gh-1))
        half = x2 - cx
        coefficient = 1
        for x in range(x1, x2 + 1):
            for y in range(y1, y2 + 1):
                v = self.grid[y][x]
                if v:
                    if half > 0:
                        coefficient = 1 / max(((cx - x)) ** 2 + ((cy - y)) ** 2, 1)                    
                    out += v.normalized() * coefficient # instead of here?

        return out.normalized()

    def walk_field(self, pos, distance):
        walked = 0
        p = pos - self.offset
        iterations = 0
        while walked < distance:
            step = min(GRIDSIZE, distance)
            p += self.get_vector(p + self.offset, 5) * step
            walked += step
            iterations += 1
            if iterations > distance * 2:
                print("walk_field hit way too many iterations, exiting with None")
                return None
        return p + self.offset
