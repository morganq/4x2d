import states


class Scene:
    def __init__(self, game):
        self.game = game
        self.sm = None

    def update(self, dt):
        if self.sm:
            self.sm.state.update(dt)

    def render(self):
        return []

    def take_input(self, inp, event):
        if self.sm:
            self.sm.state.take_input(inp, event)
