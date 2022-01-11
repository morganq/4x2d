import button
import panel
import text
import pygame
V2 = pygame.math.Vector2


class PausePanel(panel.Panel):
    def __init__(self, pos, panel_for, on_resume, on_quit):
        super().__init__(pos, panel_for)

        self.add(text.Text("- Paused -", "big", V2(0,0), multiline_width=120), V2(0,0))

        self.add(button.Button(V2(0,0), "Resume", "small", on_resume), V2(0, 40))
        self.on_quit = on_quit
        self.quit_button = button.Button(V2(0,0), "Give Up", "small", self.verify_quit)
        self.add(self.quit_button, V2(0, 60))

        self.redraw()

    def verify_quit(self):
        if self.quit_button.text == "Give Up":
            self.quit_button.text = "Really Give Up?"
            self.quit_button._generate_image(True)
        else:
            self.on_quit()
