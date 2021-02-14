class Machine:
    def __init__(self, state):
        self.state = state
        self.state.enter()

    def transition(self, other):
        self.state.exit()
        self.state = other
        self.state.enter()

class State:
    def __init__(self, scene):
        self.scene = scene

    def take_input(self, input, event):
        pass

    def enter(self):
        pass

    def exit(self):
        pass

    def update(self, dt):
        pass