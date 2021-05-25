import math
from helper import clamp

class ObjGrid:
    def __init__(self, width, height, grid_size):
        self.grid = []
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.all_objects = []

    def generate_grid(self, objects):
        self.all_objects = []
        self.grid = []
        for y in range(math.ceil(self.height / self.grid_size)):
            self.grid.append([])
            for x in range(math.ceil(self.width / self.grid_size)):
                self.grid[-1].append([])

        for obj in objects:
            cx = clamp(obj.pos.x // self.grid_size, 0, len(self.grid[0]) - 1)
            cy = clamp(obj.pos.y // self.grid_size, 0, len(self.grid) - 1)
            self.grid[int(cy)][int(cx)].append(obj)
            self.all_objects.append(obj)

    def get_objects_near(self, pos, radius):
        x1 = clamp(math.floor((pos.x - radius) / self.grid_size), 0, len(self.grid[0]) - 1)
        x2 = clamp(math.ceil((pos.x + radius) / self.grid_size), 0, len(self.grid[0]) - 1)
        y1 = clamp(math.floor((pos.y - radius) / self.grid_size), 0, len(self.grid) - 1)
        y2 = clamp(math.ceil((pos.y + radius) / self.grid_size), 0, len(self.grid) - 1)

        objs = []
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                objs.extend(self.grid[y][x])
                
        return objs
