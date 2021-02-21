import pygame
import game
from v2 import V2

class SpriteBase(pygame.sprite.DirtySprite):
    def __init__(self, pos):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = None
        self._width = 0
        self._height = 0
        if isinstance(pos, V2):
            self._pos = pos
        else:
            self._pos = V2(*pos)
        self.offset = (0,0)
        self._recalc_rect()

        self.is_mouse_over = False
        self.is_mouse_down = False

        self.selectable = False
        self.dirty = 2

        self.collidable = False
        self.collision_radius = 0

    def _recalc_rect(self):
        self.rect = pygame.Rect(
            self._pos.x - self._width * self.offset[0],
            self._pos.y - self._height * self.offset[1],
            self._width, self._height)

    @property
    def width(self):
        return self._width

    @property
    def height(self):
        return self._height

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if isinstance(value, V2):
            self._pos = value
        else:
            self._pos = V2(*value)
        self._recalc_rect()

    @property
    def x(self):
        return self._pos.x

    @x.setter
    def x(self, value):
        self._pos = V2(value, self._pos.y)
        self._recalc_rect()

    @property
    def y(self):
        return self._pos.y

    @y.setter
    def y(self, value):
        self._pos = V2(self._pos.x, value)
        self._recalc_rect()

    def on_mouse_exit(self, pos): pass
    def on_mouse_enter(self, pos): pass
    def on_mouse_down(self, pos): pass
    def on_mouse_up(self, pos): pass
    def on_drag(self, pos): pass

    def get_selection_info(self): return None

    def update(self, dt):
        pass

    def collide(self, other):
        pass