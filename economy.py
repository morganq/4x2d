from colors import *


RESOURCES = ['iron','ice','gas']
RESOURCE_COLORS = {
    'iron':PICO_WHITE,
    'ice':PICO_BLUE,
    'gas':PICO_PINK,
}

class Resources:
    def __init__(self, iron=0, ice=0, gas=0):
        self.values = {'iron':iron, 'ice':ice, 'gas':gas}

    @property
    def ice(self): return self.values['ice']

    @property
    def gas(self): return self.values['gas']

    @property
    def iron(self): return self.values['iron']        