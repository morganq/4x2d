import pygame
import game

class SpriteBase(pygame.sprite.DirtySprite):
    def __init__(self, pos):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = None
        self._width = 0
        self._height = 0
        self._x = pos[0]
        self._y = pos[1]        
        self.offset = (0,0)    
        self._recalc_rect()

        self.is_mouse_over = False
        self.is_mouse_down = False

        self.selectable = False
        self.dirty = 2

    def _recalc_rect(self):
        self.rect = pygame.Rect(
            self._x - self._width * self.offset[0],
            self._y - self._height * self.offset[1],
            self._width, self._height)

    @property
    def x(self):
        return self._x
        self._recalc_rect()

    @x.setter
    def x(self, value):
        self._x = value
        

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self._recalc_rect()

    def on_mouse_exit(self, pos): pass
    def on_mouse_enter(self, pos): pass
    def on_mouse_down(self, pos): pass
    def on_mouse_up(self, pos): pass

    def update(self, dt):
        pass