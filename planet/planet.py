from colors import PICO_GREYPURPLE, PICO_YELLOW
import pygame
import spritebase
import framesprite

class Planet(framesprite.FrameSprite):
    def __init__(self, pos, size, resources):
        framesprite.FrameSprite.__init__(self, pos, None, 1)
        self.object_type = "planet"
        self.size = size
        self.resources = resources
        self.owning_civ = None
        self.buildings = []
        self.population = 0
        self.ships = {}

        self.selectable = True
        self.selection_radius = self.size + 14
        self.offset = (0.5, 0.5)
        self._generate_frames()

    def change_owner(self, civ):
        self.owning_civ = civ
        self._generate_frames()

    def _generate_frame(self, border = False):
        radius = self.size + 8
        padding = 8
        cx,cy = radius + padding, radius + padding
        self._width = radius * 2 + padding * 2
        self._height = radius * 2 + padding * 2
        frame = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        border_radius = 2 if border else 1
        color = self.owning_civ.color if self.owning_civ else PICO_YELLOW

        pygame.draw.circle(frame, color, (cx,cy), radius + border_radius)    
        pygame.draw.circle(frame, PICO_GREYPURPLE, (cx,cy), radius)
        return frame

    def _generate_frames(self):
        inactive = self._generate_frame(False)
        hover = self._generate_frame(True)
        w = inactive.get_width()
        h = inactive.get_height()
        self._sheet = pygame.Surface((w * 2, h), pygame.SRCALPHA)
        self._sheet.blit(inactive, (0,0))
        self._sheet.blit(hover, (w,0))
        self._width = w
        self._height = h
        self._frame_width = w
        self.frame = 0
        self._recalc_rect()

    def on_mouse_enter(self, pos):
        self.frame = 1
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self.frame = 0
        return super().on_mouse_exit(pos)

    def get_selection_info(self):
        return {"type":"planet","planet":self}