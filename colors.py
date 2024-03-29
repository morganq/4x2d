import sys

PICO_WHITE = (255,241,232)
PICO_DARKGREEN = (0, 135, 81)
PICO_ORANGE = (255,163,0)
PICO_DARKBLUE = (29,43,83)
PICO_BLUE = (41,173,255)
PICO_RED = (255,0,77)
PICO_PURPLE = (126,37,83)
PICO_BLACK = (0,0,0)
PICO_DARKGRAY = (95, 87, 79)
PICO_LIGHTGRAY = (194, 195, 199)
PICO_YELLOW = (255,236,39)
PICO_PINK = (255,119, 168)
PICO_GREEN = (0, 228, 54)
PICO_GREYPURPLE = (131,118,156)
PICO_BROWN = (171, 82, 54)
PICO_SKIN = (255,204,170)

ALL_COLORS = [
    PICO_WHITE,
    PICO_DARKGREEN,
    PICO_ORANGE,
    PICO_DARKBLUE,
    PICO_BLUE,
    PICO_RED,
    PICO_PURPLE,
    PICO_BLACK,
    PICO_DARKGRAY,
    PICO_LIGHTGRAY,
    PICO_YELLOW,
    PICO_PINK,
    PICO_GREEN,
    PICO_GREYPURPLE,
    PICO_BROWN,
    PICO_SKIN,
]

DARKEN_COLOR = {
    PICO_GREEN:PICO_DARKGREEN,
    PICO_BLUE:PICO_DARKBLUE,
    PICO_PINK:PICO_PURPLE,
    PICO_RED:PICO_PURPLE,
    PICO_WHITE:PICO_LIGHTGRAY,
    PICO_LIGHTGRAY:PICO_DARKGRAY,
    PICO_GREYPURPLE:PICO_BLACK,
    PICO_ORANGE:PICO_BROWN,
    PICO_BROWN:PICO_PURPLE,
    PICO_YELLOW:PICO_ORANGE,
    PICO_DARKGRAY:PICO_PURPLE,
    PICO_PURPLE:PICO_BLACK,
    PICO_SKIN:PICO_ORANGE,
    PICO_BLACK:PICO_BLACK,
    PICO_DARKBLUE:PICO_BLACK
}

LIGHTEN_COLOR = {
    PICO_PURPLE:PICO_PINK,
    PICO_DARKBLUE:PICO_BLUE,
    PICO_DARKGRAY:PICO_LIGHTGRAY,
    PICO_GREYPURPLE:PICO_LIGHTGRAY,
    PICO_LIGHTGRAY:PICO_WHITE,
    PICO_BROWN:PICO_ORANGE,
    PICO_ORANGE:PICO_YELLOW,
    PICO_WHITE:PICO_WHITE,
    PICO_YELLOW:PICO_WHITE,
    PICO_BLUE:PICO_WHITE
}

LIGHTS = [
    PICO_WHITE, PICO_LIGHTGRAY, PICO_YELLOW, PICO_SKIN
]
MEDS = [
    PICO_BLUE, PICO_GREEN, PICO_ORANGE, PICO_RED, PICO_PINK, PICO_GREYPURPLE
]
DARKS = [
    PICO_BROWN, PICO_PURPLE, PICO_DARKGRAY, PICO_DARKGREEN, PICO_DARKBLUE
]

for color in ALL_COLORS:
    setattr(sys.modules[__name__],"%s_BACKGROUND", (int(c / 2) for c in color))
