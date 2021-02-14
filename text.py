import pygame
import pygame.freetype
from resources import resource_path

pygame.freetype.init()

FONTS = {
    'small':pygame.freetype.Font(resource_path("assets/Minecraftia-Regular.ttf"), 8),
    'big':pygame.freetype.Font(resource_path("assets/upheavtt.ttf"), 20),
    'huge':pygame.freetype.Font(resource_path("assets/upheavtt.ttf"), 30)
}



for font in FONTS.values():
    font.antialiased = False

class Text(pygame.sprite.Sprite):
    type = None
    def __init__(self, text, size, pos, color = (247, 249, 223), border=True):
        pygame.sprite.Sprite.__init__(self)
        self._text = text
        self.size = size
        self.pos = pos
        self.color = color
        self.border = border
        self.set_text(text)
        
    def set_text(self, text):
        self._text = text
        self.update()

    def update(self):
        f = FONTS[self.size]
        r = f.get_rect(self._text)
        self.image = pygame.Surface((r[2] + 2, r[3] + 2), flags=pygame.SRCALPHA)
        if self.border:
            f.render_to(self.image, (0,1), self._text, (42,17,81), (0,0,0,0))
            f.render_to(self.image, (1,0), self._text, (42,17,81), (0,0,0,0))
            f.render_to(self.image, (2,1), self._text, (42,17,81), (0,0,0,0))
            f.render_to(self.image, (1,2), self._text, (42,17,81), (0,0,0,0))
        f.render_to(self.image, (1,1), self._text, self.color, (0,0,0,0))
        self.rect = (self.pos[0], self.pos[1], self.image.get_rect()[2], self.image.get_rect()[3])

    def set_pos(self, x, y):
        self.pos = (x,y)
        self.rect = (self.pos[0], self.pos[1], self.image.get_rect()[2], self.image.get_rect()[3])
