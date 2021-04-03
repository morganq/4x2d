import pygame
from colors import *
from scene import Scene
from background import Background
from spritebase import SpriteBase
import text
from v2 import V2
from helper import clamp

class LEObject(SpriteBase):
    def __init__(self, pos, obj_type):
        super().__init__(pos)
        self.radius = 1
        self.size = 1
        self.obj_type = obj_type
        self.offset = (0.5, 0.5)
        self.desc = text.Text("", "small", self.pos, color=PICO_BLACK, shadow=PICO_WHITE)
        self.data = {}
        self._generate_image()

    def set_radius(self, rad):
        rad /= 4
        if self.obj_type.endswith('planet'):
            self.size = clamp(rad - 8,1,10)
            self.desc.set_text(str(int(self.size)))
            self.radius = self.size + 8
        else:
            self.radius = clamp(rad, 5, 25)
        self._generate_image()

    def _generate_image(self):
        w = 50
        h = 50
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)

        color = {
            'my_planet':PICO_GREEN,
            'enemy_planet':PICO_RED,
            'neutral_planet':PICO_YELLOW,
            'hazard':PICO_LIGHTGRAY
        }[self.obj_type]

        pygame.draw.circle(self.image, color, (w/2,h/2), self.radius, 0)
        self._width = w
        self._height = h
        self._recalc_rect()

    def kill(self):
        self.desc.kill()
        super().kill()



class LevelEditorScene(Scene):
    def __init__(self, game, options=None):
        Scene.__init__(self, game)
        self.current_object_type = 'my_planet'
        self.current_object_resources = [10,0,0]
        self.current_object_resources_index = 0
        self.current_object = None
    
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.background_group.add(Background(V2(0,0)))

    def take_input(self, inp, event):
        if inp == "click":
            o = LEObject(event.gpos, self.current_object_type)
            self.game_group.add(o)
            self.ui_group.add(o.desc)
            self.current_object = o
            o.data['resources'] = self.current_object_resources[::]
            self.current_object_resources_index = 0

        if inp == "unclick":
            self.current_object = None

        if inp == "mouse_drag":
            if self.current_object:
                d = (event.gpos - self.current_object.pos).magnitude()
                self.current_object.set_radius(d)

        if inp == "other":
            if event.key == pygame.K_q: self.current_object_type = "my_planet"
            if event.key == pygame.K_w: self.current_object_type = "neutral_planet"
            if event.key == pygame.K_e: self.current_object_type = "enemy_planet"
            if event.key == pygame.K_r: self.current_object_type = "hazard"
            if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                val = (event.key - pygame.K_0)
                if event.key == pygame.K_0: val = 10
                self.current_object_resources[self.current_object_resources_index] = val
                self.current_object_resources_index = (self.current_object_resources_index + 1) % 3
            if event.key == pygame.K_BACKSPACE:
                try: self.game_group.sprites()[-1].kill()
                except: pass

        return super().take_input(inp, event)    

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        text.render_multiline_to(self.game.screen, (3,3), self.current_object_type, "small", PICO_WHITE)
        text.render_multiline_to(self.game.screen, (3,16), str(self.current_object_resources), "small", PICO_WHITE)
        return super().render()