from framesprite import FrameSprite


class TimeLoop(FrameSprite):
    def __init__(self, pos, sprite_sheet, frame_width):
        super().__init__(pos, sprite_sheet=sprite_sheet, frame_width=frame_width)
        self.time = 0

    def update(self, dt):
        self.time += dt
        self.frame = int((self.time * 4) % 8)
        return super().update(dt)
