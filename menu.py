import game
import joyresolver
import slider
import text
from colors import *
from helper import clamp
from v2 import V2


class MenuOption:
    def __init__(self, label) -> None:
        self.label = label
        self.on_hover = None
        self.on_unhover = None

    def create(self, scene, pos):
        self.pos = pos
        self.title = text.Text(self.label, "small", self.pos, onhover=self.on_hover, multiline_width=999)
        self.title.on("mouse_exit", lambda a,b:self.on_unhover())   
        scene.ui_group.add(self.title)

    def destroy(self):
        self.title.kill()

    def input_confirm(self):
        pass

    def input_direction(self, direction):
        pass
    
    def hover(self):
        self.title.color = PICO_YELLOW
        self.title.update_image()

    def unhover(self):
        self.title.color = PICO_WHITE
        self.title.update_image()

class ButtonMenuOption(MenuOption):
    def __init__(self, label, on_confirm) -> None:
        super().__init__(label)
        self.on_confirm = on_confirm

    def create(self, scene, pos):
        super().create(scene, pos)
        self.title.on("mouse_down", lambda a,b:self.input_confirm())

    def input_confirm(self):
        self.on_confirm()

class SliderMenuOption(MenuOption):
    def __init__(self, label, minimum, maximum, value, on_change) -> None:
        super().__init__(label)
        self.minimum = minimum
        self.maximum = maximum
        self.value = value
        self.on_change = on_change

    def create(self, scene, pos):
        super().create(scene, pos)
        self.slider = slider.Slider(pos + V2(80, 0), 150, self.minimum, self.maximum, self.on_change, value = self.value)
        self.slider.on("mouse_enter", lambda a,b:self.on_hover)
        self.slider.on("mouse_exit", lambda a,b:self.on_unhover)
        scene.ui_group.add(self.slider)

    def destroy(self):
        self.slider.kill()
        return super().destroy()

    def input_direction(self, direction):
        if direction == "left":
            self.slider.set_value(self.slider.value - 1)
        if direction == "right":
            self.slider.set_value(self.slider.value + 1)

class ChoiceMenuOption(MenuOption):
    def __init__(self, label, choices, value, on_change) -> None:
        super().__init__(label)
        self.choices = choices
        try:
            self.index = self.choices.index(value)
        except:
            self.index = 0
        self.value = value
        self.on_change = on_change
        
    def create(self, scene, pos):
        super().create(scene, pos)
        self.title.on("mouse_down", lambda a,b:self.input_confirm())
        self.choice_text = text.Text("", "small", self.pos + V2(80, 0), PICO_BLUE)
        scene.ui_group.add(self.choice_text)
        self._update_choice_text()

    def destroy(self):
        self.choice_text.kill()
        return super().destroy()

    def _update_choice_text(self):
        self.choice_text.set_text("< %s >" % str(self.value))

    def input_confirm(self):
        self.input_direction("right")

    def input_direction(self, direction):
        if direction == "right":
            self.index = (self.index + 1) % len(self.choices)
            self.value = self.choices[self.index]
            self._update_choice_text()
            self.on_change(self.value)

        if direction == "left":
            self.index = (self.index - 1) % len(self.choices)
            self.value = self.choices[self.index]
            self._update_choice_text()
            self.on_change(self.value)            


class Menu:
    def __init__(self, scene, pos, options = None) -> None:
        self.scene = scene
        self.pos = pos
        if options is None:
            self.options = []
        for option in self.options:
            self.add_option(option)

        self.hover_option_index = None

        self.joy = joyresolver.JoyResolver(self.on_direction_press)

    def clear(self):
        for option in self.options:
            option.destroy()
        self.options = []        

    def reconstruct(self, pos):
        for option in self.options:
            option.destroy()

        self.pos = pos
        old_options = self.options[::]
        self.options = []

        for option in old_options:
            self.add_option(option)

        if self.hover_option_index is not None:
            self.on_option_hover(self.hover_option_index)

    def on_direction_press(self, direction):
        if self.hover_option_index is None:
            self.on_option_hover(0)
        elif direction == "down":
            self.on_option_hover(clamp(self.hover_option_index + 1, 0, len(self.options) - 1))
        elif direction == "up":
            self.on_option_hover(clamp(self.hover_option_index - 1, 0, len(self.options) - 1))
        else:
            self.options[self.hover_option_index].input_direction(direction)

    def on_option_hover(self, index):
        if self.hover_option_index is not None:
            old_hover = self.options[self.hover_option_index]
            old_hover.unhover()

        self.options[index].hover()
        self.hover_option_index = index

    def on_option_unhover(self, index):
        if self.hover_option_index is not None:
            self.options[self.hover_option_index].unhover()
            self.hover_option_index = None

    def add_option(self, option):
        index = len(self.options)
        pos = self.pos + V2(0, index * 26)
        option.on_hover = lambda x:self.on_option_hover(index)
        option.on_unhover = lambda x:self.on_option_unhover(index)
        option.create(self.scene, pos)
        self.options.append(option)
        if index == 0 and game.Game.inst.input_mode == "joystick" and self.hover_option_index is None:
            self.on_option_hover(0)

    def take_input(self, input, event):
        if input == "joymotion":
            self.joy.take_input(input, event)
        if input == "confirm":
            if self.hover_option_index is not None:
                self.options[self.hover_option_index].input_confirm()
