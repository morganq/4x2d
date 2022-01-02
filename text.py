import re

import pygame
import pygame.freetype

import game
import spritebase
from colors import *
from resources import resource_path

pygame.freetype.init()

FONTS = {
    'tiny':pygame.freetype.Font(resource_path("assets/Pixeled.ttf"), 5),
    'small':pygame.freetype.Font(resource_path("assets/Minecraftia-Regular.ttf"), 8),
    'medium':pygame.freetype.Font(resource_path("assets/Pixeled.ttf"), 10),
    'big':pygame.freetype.Font(resource_path("assets/upheavtt.ttf"), 20),
    'huge':pygame.freetype.Font(resource_path("assets/m12.ttf"), 30),
    'pixolde':pygame.freetype.Font(resource_path("assets/Pixolde-Italic.ttf"), 16),
    'logo':pygame.freetype.Font(resource_path("assets/conthrax-sb.ttf"), 20)
}

PRELOADED_SYMBOLS = {}

def preload():
    mapping = {'tiny': 'sm', 'small': 'sm', 'medium':'md', 'big':'md', 'huge':'lg', 'pixolde':'md', 'logo':'md'}
    for size, font in FONTS.items():
        sy = {}
        sy['left'] = ('assets/mouse_left.png', None)
        sy['right'] = ('assets/mouse_right.png', None)
        sy['drag'] = ('assets/mouse_drag.png', None)
        sy['ps_square'] = ('assets/ps_%s.png' % mapping[size], 1)
        sy['ps_triangle'] = ('assets/ps_%s.png' % mapping[size], 2)
        sy['ps_circle'] = ('assets/ps_%s.png' % mapping[size], 3)
        sy['ps_x'] = ('assets/ps_%s.png' % mapping[size], 0)
        sy['xbox_square'] = ('assets/xbox_%s.png' % mapping[size], 2)
        sy['xbox_triangle'] = ('assets/xbox_%s.png' % mapping[size], 3)
        sy['xbox_circle'] = ('assets/xbox_%s.png' % mapping[size], 1)
        sy['xbox_x'] = ('assets/xbox_%s.png' % mapping[size], 0)
        PRELOADED_SYMBOLS[size] = {}
        for k,v in sy.items():
            PRELOADED_SYMBOLS[size][k] = (pygame.image.load(resource_path(v[0])), v[1])


for name,font in FONTS.items():
    font.antialiased = False
    font.pad = True
    print(name, font.get_sized_height(), font.get_sized_glyph_height(), font.get_sized_ascender(), font.get_sized_descender())

class Text(spritebase.SpriteBase):
    type = None
    def __init__(self, text, size, pos, color = PICO_WHITE, border=False, multiline_width = 80, center = True, shadow=False, offset = None, onclick = None, onhover = None, flash_color = None):
        spritebase.SpriteBase.__init__(self, pos)
        self._text = text
        self.size = size
        self.color = color
        self.border = border
        self.shadow = shadow
        self.center = center
        self.multiline_width = multiline_width
        self.offset = offset or (0,0)
        self.onclick = onclick
        self.onhover = onhover
        self.flash_time = 0
        self.flash_color = flash_color
        if flash_color:
            self.flash_color = flash_color
            self.flash_time = 0.125
        if self.onclick or self.onhover:
            self.selectable = True
        self.set_text(text)

    def set_text(self, text):
        self._text = text
        self.update_image()

    def update_image(self):
        color = self.color
        if self.flash_time > 0:
            color = self.flash_color
        text_image = render_multiline(self._text, self.size, color, self.multiline_width, self.center)
        w, h = text_image.get_size()
        if self.shadow:
            h += 1
            self.image = pygame.Surface((w,h), pygame.SRCALPHA)
            shadow_image = render_multiline(self._text, self.size, self.shadow, self.multiline_width, self.center)
            self.image.blit(shadow_image, (0,1))
            self.image.blit(text_image, (0,0))
        elif self.border:
            h += 2
            w += 2
            self.image = pygame.Surface((w,h), pygame.SRCALPHA)
            border_image = render_multiline(self._text, self.size, self.border, self.multiline_width, self.center)
            self.image.blit(border_image, (0,1))
            self.image.blit(border_image, (2,1))
            self.image.blit(border_image, (1,0))
            self.image.blit(border_image, (1,2))
            self.image.blit(text_image, (1,1))            
        else:
            self.image = text_image
        
        self._width = w
        self._height = h
        self._recalc_rect()

    def update(self, dt):
        if self.flash_time > 0:
            self.flash_time -= dt
            if self.flash_time <= 0:
                self.update_image()
        return super().update(dt)

    def on_mouse_enter(self, pos):
        if self.onhover:
            self.onhover(True)
            return True
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        if self.onhover:
            self.onhover(False)
            return True
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        if self.onclick:
            self.onclick()
        super().on_mouse_down(pos)
        return True

def render_multiline_to(surface, pos, text, size, color, wrap_width=None, center=True):
    s = render_multiline(text, size, color, wrap_width, center)
    surface.blit(s, pos)

parens_re = re.compile("\((.+?)\).*")
TEXT_COLORS = {'!':PICO_RED,'^':PICO_GREEN, '>': PICO_YELLOW}
HEIGHTS = {'tiny':12, 'small':12, 'medium':14, 'big':18, 'huge':28, 'bm_army':12, 'pixolde':16, 'logo':50}
Y_OFFSETS = {'tiny':0, 'small': -2, 'medium': 0, 'big': -4, 'huge':0, 'bm_army':0, 'pixolde':0, 'logo':0}
Y_SYMBOL_OFFSETS = {'tiny':0, 'small': 0, 'medium': 0, 'big': 0, 'huge':1, 'bm_army':0, 'pixolde':0, 'logo':0}

SYMBOLS = [
    'left', 'right', 'drag', 'x', 'square', 'triangle', 'circle'
]

def get_symbol(size, name):
    if name in ['x', 'square', 'triangle', 'circle']:
        is_ps = False
        if game.Game.inst:
            joys = game.Game.inst.joysticks
            is_ps = joys and joys[0].get_numbuttons() == 14

        if is_ps:
            name = "ps_%s" % name
        else:
            name = "xbox_%s" % name
        symbol_img, frame = PRELOADED_SYMBOLS[size][name]
        w = symbol_img.get_width() / 4
        x = w * frame
        h = symbol_img.get_height()
        frame_image = symbol_img.subsurface((x,0,w,h))
    else:
        frame_image, _ = PRELOADED_SYMBOLS[size][name]
    return frame_image

# Takes some text, returns a list of groups.
# Group is {'color':whatever, 'text':body}
def get_groups(line):
    groups = [{'color':None, 'body':""}]
    x = 0

    def add_group(grp):
        if groups[-1]['body'] == "":
            groups[-1] = grp
        else:
            groups.append(grp)

    while x < len(line):
        if line[x] == "[":
            if "]" in line:
                if line[x+1] in TEXT_COLORS.keys():
                    color = line[x+1]
                    add_group({'color':TEXT_COLORS[color], 'body':""})
                    x += 1
                else:
                    add_group({'color':PICO_WHITE, 'body':""})
            else:
                return groups
        elif line[x] == "]":
            add_group({'color':None, 'body':""})
        elif line[x] == "\n":
            add_group({'color':groups[-1]['color'], 'body':"\n"})
        else:
            groups[-1] = {'color':groups[-1]['color'], 'body':groups[-1]['body'] + line[x]}
        x += 1
    return groups

# Given a list of groups, returns a list of words.
# A word looks like
# {'type':'text', 'body':'hello', 'color':PICO_WHITE}, or
# {'type':'symbol', 'name':'left'}
def get_words(groups):
    # Output list
    words = []

    # Dict maps '*left*' -> 'left'
    symbol_names_w_stars = {"*%s*"%s:s for s in SYMBOLS}
    for group in groups:
        # A group's body is either text, or a symbol name with * around it
        # 1. Symbol
        if group['body'] in symbol_names_w_stars:
            word = {'type':'symbol', 'name':symbol_names_w_stars[group['body']]}
            words.append(word)
            
        # 2. Text
        else:
            group_words = [w + " " for w in group['body'].split(" ") if w]
            for word in group_words:
                word = {'type':'text', 'body':word, 'color':group['color']}
                words.append(word)

    return words

def get_word_layout(words, size, wrap_width=None, center=True):
    result = {}
    f = FONTS[size]
    basic_char_height = f.get_sized_height()
    height_per_line = int(basic_char_height * 1)    
    left_x = 0
    baseline_y = f.get_rect("M").height + Y_OFFSETS[size]
    width = 0
    height = height_per_line    
    layout = []
    lines = [[]]
    # Go through each word and "render" it but just find the position
    for word in words:
        ### Is it a symbol? ###
        if word['type'] == 'symbol':
            image = get_symbol(size, word['name'])
            w,h = image.get_size()
            wx2 = left_x + w

            # If we have word wrap, and our right edge is beyond
            # the wrap border, and we have written at least one
            # word to this line so far, advance to the next line            
            if wrap_width and wx2 > wrap_width and lines[-1]:
                left_x = 0
                baseline_y += height_per_line
                lines.append([])                
            my = baseline_y - f.get_rect("M").height // 2
            spacing = int(w / 6) + 2
            rect = pygame.Rect(left_x, my - h // 2, w + spacing, h)
            lines[-1].append({'word':word, 'rect':rect})
            # Adjust running variables
            left_x += rect.width
            width = max(left_x, width)
            height = max(baseline_y, rect.y + rect.height)

        ### Is it text? ###
        elif word['type'] == 'text':
            # Get the size of the word
            rect = f.get_rect(word['body'])
            
            # Same word wrap logic as for symbols
            wx2 = left_x + rect.x + rect.width
            is_newline = '\n' in word['body']
            if (wrap_width and wx2 > wrap_width and lines[-1]) or is_newline:
                left_x = 0
                baseline_y += height_per_line
                lines.append([])

            if is_newline:
                continue
            wx = left_x + rect.x
            wy = baseline_y - rect.height 
            ww = rect.width
            wh = rect.height
            lines[-1].append({'word':word, 'rect':pygame.Rect(wx,wy,ww,wh)})
            # Adjust running variables
            left_x += ww
            width = max(left_x, width)
            height = baseline_y
    for line in lines:
        for wordspec in line:
            layout.append(wordspec)
    return {
        'layout':layout,
        'rect':pygame.Rect(0, 0, width, height)
    }

def render_multiline(text, size, color, wrap_width=None, center=True):
    return render_multiline_extra(text, size, color, wrap_width, center)[0]

def render_multiline_extra(text, size, color, wrap_width=None, center=True):
    words = get_words(get_groups(text))
    layout = get_word_layout(words, size=size, wrap_width=wrap_width, center=center)
    surf = pygame.Surface(layout['rect'].size, pygame.SRCALPHA)
    #surf.fill((255,0,255))
    f = FONTS[size]
    for wordspec in layout['layout']:
        word = wordspec['word']
        rect = wordspec['rect']
        if word['type'] == 'symbol':
            image = get_symbol(size, word['name'])
            surf.blit(image, rect.topleft)

        if word['type'] == 'text':
            word_color = word['color'] or color
            try:
                f.render_to(surf, rect.topleft, word['body'], word_color)
            except:
                print("TEXT RENDERING ERROR", word)

    return (surf, layout)
    
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((800,600))
    screen.fill(PICO_BLACK)

    preload()

    body = "[*left*] Ships gain [^+33%] move\n[*x*] speed and [^+33%] rate [*drag*] of fire. Every ` time you [*square*] issue an order, [!-5] seconds of oxygen . ` / *"

    groups = get_groups(body)
    words = get_words(groups)
    print(groups)
    print(words)

    layout = get_word_layout(words, "small")
    print(layout['rect'])
    for wordspec in layout['layout']:
        print(wordspec)

    surf = render_multiline(body, "big", PICO_WHITE, wrap_width=180)
    screen.blit(surf, (10,10))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.display.update()
