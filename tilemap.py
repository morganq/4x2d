import pygame
import math
import csv
from resources import resource_path

class Tilemap(pygame.sprite.Sprite):
    def __init__(self, tile_size, num_columns, num_rows, tile_images, use_zero = False):
        pygame.sprite.Sprite.__init__(self)

        self.tile_size = tile_size
        self.num_columns = num_columns
        self.num_rows = num_rows
        self.tile_images = tile_images
        self.use_zero = use_zero

        self.image = pygame.Surface((self.tile_size * self.num_columns, self.tile_size * self.num_rows), flags=pygame.SRCALPHA)
        self.rect = self.image.get_rect()

        self._dirty_rects = []
        self.clear_grid()
        
    def invalidate(self):
        self._dirty_rects = [pygame.Rect(
                0, 0,
                self.tile_size * self.num_columns, self.tile_size * self.num_rows
            )]

    def clear_grid(self):
        self._grid = []
        for row in range(self.num_rows):
            self._grid.append([])
            for col in range(self.num_columns):
                self._grid[-1].append(-1)

        self._dirty_rects = [pygame.Rect(
                0, 0,
                self.tile_size * self.num_columns, self.tile_size * self.num_rows
            )]
        self.update_image()

    def load(self, filename):
        with open(resource_path(filename)) as f:
            reader = csv.reader(f)
            for y,row in enumerate(reader):
                for x,cell in enumerate(row):
                    #if cell == -1: cell = 0
                    self._grid[y][x] = int(cell)
        self._dirty_rects = [pygame.Rect(
                0, 0,
                self.tile_size * self.num_columns, self.tile_size * self.num_rows
            )]
        self.update_image()        

    def set_data(self, data):
        self._grid = data
        self._dirty_rects = [pygame.Rect(
                0, 0,
                self.tile_size * self.num_columns, self.tile_size * self.num_rows
            )]
        self.update_image()

    def set_tile(self, x, y, tile):
        self._grid[y][x] = tile
        self._dirty_rects.append(pygame.Rect(
            x * self.tile_size, y * self.tile_size,
            self.tile_size, self.tile_size
        ))
        self.update_image()

    def update_image(self):
        for rect in self._dirty_rects:
            pygame.draw.rect(self.image, (0,0,0,0), rect, 0) # Make the dirty area transparent (or bg color?)
            
            # Find all the tiles that are inside this dirty rect
            x1 = rect.left // self.tile_size
            y1 = rect.top // self.tile_size
            x2 = math.ceil(rect.right / self.tile_size)
            y2 = math.ceil(rect.bottom / self.tile_size)
            # Paint them
            for x in range(x1, x2):
                for y in range(y1, y2):
                    self.paint_tile(x,y)
        self._dirty_rects = []

    def paint_tile(self, x, y):
        tile_index = self._grid[y][x]
        if tile_index == -1 or (tile_index == 0 and not self.use_zero):
            return
        self.image.blit(
            self.tile_images, # Source
            (x * self.tile_size, y * self.tile_size), # Dest point
            (self.tile_size * tile_index, 0, self.tile_size, self.tile_size) # Source rect
        )
