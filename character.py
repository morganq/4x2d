import pygame
import framesprite
import game
import random
import particle

class Character(framesprite.FrameSprite):
    type = "character"
    def __init__(self, sheet, gx, gy, width, x_offset=0):
        self.gx = gx
        self.gy = gy
        x = gx * game.TILESIZE
        y = gy * game.TILESIZE
        framesprite.FrameSprite.__init__(self, sheet, width)
        self.x_offset = x_offset
        self.rect = (x + self.x_offset, y - 6, width, self._sheet.get_size()[1])
        self.activated = False
        self.last_move_direction = random.randint(0,min(4, self._sheet.get_size()[0] // width // 2) - 1)
        self.step_animation()

        self.must_finish_step = False
        self.just_stepped_t = 0
        

    def step_animation(self):
        base_frame = self.last_move_direction * 2
        if not self.activated:
            self.set_frame((self._frame + 1) % 2 + base_frame)

    def update_direction(self):
        base_frame = self.last_move_direction * 2
        self.set_frame((self._frame % 2) + base_frame)
        
    def interact(self, state, worker):
        return False        

    def try_push(self, state, offset):
        pass

    def set_starting_dir(self, roads):
        if roads[self.gy][self.gx-1]:
            self.last_move_direction = 2
        elif roads[self.gy][self.gx+1]:
            self.last_move_direction = 0
        elif roads[self.gy+1][self.gx]:
            self.last_move_direction = 1
        elif roads[self.gy-1][self.gx]:
            self.last_move_direction = 3
        self.update_direction()

    def update(self, dt):
        if self.must_finish_step:
            self.just_stepped_t -= dt
            if self.just_stepped_t <= 0:
                self.must_finish_step = False
                self.move(self.rect[0], self.rect[1] + 2)
                for i in range(4):
                    dx = random.randint(-3, 3)
                    p = particle.Particle(
                        "assets/dustcloud2.png",
                        5,
                        (self.rect[0] + self.rect[2] / 2 - 2 + dx, self.rect[1] + self.rect[3] - 3),
                        0.25 + random.random() * 0.125,
                        (dx * 1, 0))
                    self.groups()[0].add(p)

    def step(self, x, y, offset=0):
        self.move(x, y-2)
        self.just_stepped_t = (offset + 1) * 0.05
        self.must_finish_step = True