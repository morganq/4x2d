import math


class JoyResolver:
    def __init__(self, on_press) -> None:
        self.last_dir = None
        self.on_press = on_press

    def take_input(self, input, event):
        delta = event['delta']
        self.joystick_state = delta
        if delta.sqr_magnitude() > 0.75 ** 2:
            _,ang = delta.to_polar()
            ang /= math.pi / 2
            ang4 = round(ang)
            angs = {0:"right", 1:"down", 2:"left", -2:"left", -1:"up"}
            dir = angs[ang4]
            if dir != self.last_dir:
                self.last_dir = dir
                self.on_press(dir)
        else:
            self.last_dir = None
