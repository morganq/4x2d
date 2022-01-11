import pygame

V2 = pygame.math.Vector2


class SpriteBase(pygame.sprite.DirtySprite):
    def __init__(self, pos):
        pygame.sprite.DirtySprite.__init__(self)
        self.image = None
        self._width = 0
        self._height = 0
        if isinstance(pos, V2):
            self._pos = V2(pos)
        else:
            self._pos = V2(*pos)
        self._offset = (0,0)
        self._recalc_rect()

        self.is_mouse_over = False
        self.is_mouse_down = False

        self.selectable = False
        self.dirty = 2

        self.collidable = False
        self.collision_radius = 0
        self._timers = {}
        self._scrolled_offset = V2(0,0)
        self._event_handlers = []

    def on(self, event_name, callback):
        self._event_handlers.append({'event':event_name, 'callback':callback})

    def _recalc_rect(self):
        self.rect = pygame.Rect(
            self._pos.x - self._width * self.offset[0],
            self._pos.y - self._height * self.offset[1],
            self._width, self._height)

    def get_center(self):
        return V2(self.rect[0] + self.rect[2] / 2, self.rect[1]+self.rect[3] / 2)

    @property
    def wh(self):
        return V2(self._width, self._height)

    @property
    def offset(self):
        return self._offset

    @offset.setter
    def offset(self, value):
        self._offset = value
        self._recalc_rect()

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
    def apparent_pos(self):
        return self._pos + self._scrolled_offset

    @property
    def top_left(self):
        return V2(self.rect[0], self.rect[1])

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

    def dispatch_event(self, name, data):
        for cb in self._event_handlers:
            if cb['event'] == name:
                cb['callback'](self, data)

    def on_mouse_exit(self, pos):
        self.dispatch_event("mouse_exit", pos)

    def on_mouse_enter(self, pos):
        self.dispatch_event("mouse_enter", pos)

    def on_mouse_down(self, pos):
        self.dispatch_event("mouse_down", pos)

    def on_mouse_up(self, pos):
        self.dispatch_event("mouse_up", pos)

    def on_drag(self, pos):
        self.dispatch_event("drag", pos)

    def get_selection_info(self): return None

    def update(self, dt):
        for k in self._timers.keys():
            self._timers[k] += dt
        if self.image is None and self.visible:
            print("no image!", self)

    def collide(self, other):
        pass
