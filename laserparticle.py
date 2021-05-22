import line

class LaserParticle(line.Line):
    def __init__(self, start, end, color, lifetime):
        super().__init__(start, end, color)
        self.lifetime = lifetime
        self.time = 0

    def update(self, dt):
        self.time += dt
        if self.time > self.lifetime:
            self.kill()
        return super().update(dt)