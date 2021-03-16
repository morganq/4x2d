from colors import *


RESOURCES = ['iron','ice','gas']
RESOURCE_COLORS = {
    'iron':PICO_WHITE,
    'ice':PICO_BLUE,
    'gas':PICO_PINK,
}

class Resources:
    def __init__(self, iron=0, ice=0, gas=0):
        self.data = {'iron':iron, 'ice':ice, 'gas':gas}
        self.handlers = []

    def on_change(self, fn):
        self.handlers.append(fn)

    def set_resource(self, r, v):
        self.data[r] = v
        for handler in self.handlers:
            handler(r,v)

    @property
    def ice(self): return self.data['ice']
    @ice.setter
    def ice(self, value): self.set_resource('ice', value)

    @property
    def gas(self): return self.data['gas']
    @gas.setter
    def gas(self, value): self.set_resource('gas', value)

    @property
    def iron(self): return self.data['iron']   
    @iron.setter
    def iron(self, value): self.set_resource('iron', value)         