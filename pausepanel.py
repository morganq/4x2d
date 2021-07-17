import button
import panel
import text
from v2 import V2


class PausePanel(panel.Panel):
    def __init__(self, pos, panel_for, on_resume, on_quit):
        super().__init__(pos, panel_for)

        self.add(text.Text("- Paused -", "big", V2(0,0), multiline_width=120), V2(0,0))

        self.add(button.Button(V2(0,0), "Resume", "small", on_resume), V2(0, 40))
        self.add(button.Button(V2(0,0), "Save and Quit", "small", on_quit), V2(0, 60))

        self.redraw()
