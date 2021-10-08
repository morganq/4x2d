import text
from colors import *
from helper import clamp


class Typewriter(text.Text):
    def __init__(self, text, size, pos, color=PICO_WHITE, rate=20, time_offset=0, border=False, multiline_width=80, center=False, shadow=False, offset=None, onclick=None, onhover=None, flash_color=None):
        super().__init__(text, size, pos, color=color, border=border, multiline_width=multiline_width, center=center, shadow=shadow, offset=offset, onclick=onclick, onhover=onhover, flash_color=flash_color)
        self.final_surf = self.image
        self.set_text("")
        self.base_text = text
        self.time = time_offset
        self.rate = rate

    def update(self, dt):
        self.time += dt
        chars = clamp(int(self.time * self.rate), 0, len(self.base_text))
        if self._text != self.base_text:
            self.set_text(self.base_text[0:chars])
            self._width = self.final_surf.get_width()
            self._recalc_rect()
        return super().update(dt)
