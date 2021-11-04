class PlayerInputDispatcher:
    pass

class Player:
    INPUT_MOUSE = "mouse"
    INPUT_JOYSTICK = "joystick"
    def __init__(self, id, input_type, joystick_id = None) -> None:
        self.player_id = id
        self.input_type = input_type
        self.joystick_id = joystick_id
        self.joystick_mapping = {}  # Which joystick buttons are bound to which actions

    def get_horizontal_axis(self):
        return 0

    def get_vertical_axis(self):
        return 1

    def get_binding(self, button):
        return 0
