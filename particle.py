import framesprite

class Particle(framesprite.FrameSprite):
    def __init__(self, sheet, width, pos, time, vel=None):
        framesprite.FrameSprite.__init__(self, sheet, width)
        self.move(*pos)
        self.time = time
        self.initial_time = time
        if vel:
            self.xv, self.yv = vel
        else:
            self.xv, self.yv = 0,0
        self.type = "particle"

    def update(self, dt):
        self.time -= dt
        self.move(self.rect[0] + self.xv * dt, self.rect[1] + self.yv * dt)
        i = int((1 - self.time / self.initial_time) * self._num_frames)
        if self.time <= 0:
            self.kill()
        else:        
            self.set_frame(i)
