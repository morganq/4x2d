import json

import pygame

import game
import text
from background import Background
from colors import *
from helper import clamp
from levelbackground import LevelBackground
from scene import Scene
from spritebase import SpriteBase

V2 = pygame.math.Vector2


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
            self.size = clamp(rad - 8,1,10)
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
            'hazard':PICO_LIGHTGRAY,
            'crystal':PICO_BLUE
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
        self.time = 0
        self.redo_background_timer = 0
    
    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()

        self.background = LevelBackground(V2(0,0), self.game.game_resolution)
        self.background.generate_image([])
        self.background_group.add(self.background)

    def save(self):
        pass

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
            self.background.generate_image(self.game_group.sprites())

        if inp == "mouse_drag":
            if self.current_object:
                d = (event.gpos - self.current_object.pos).length()
                self.current_object.set_radius(d)

        if inp == "other":
            if event.key == pygame.K_q: self.current_object_type = "my_planet"
            if event.key == pygame.K_w: self.current_object_type = "neutral_planet"
            if event.key == pygame.K_e: self.current_object_type = "enemy_planet"
            if event.key == pygame.K_r: self.current_object_type = "hazard"
            if event.key == pygame.K_t: self.current_object_type = "crystal"
            if event.key >= pygame.K_0 and event.key <= pygame.K_9:
                val = (event.key - pygame.K_0)
                if event.key == pygame.K_0: val = 10
                self.current_object_resources[self.current_object_resources_index] = val
                self.current_object_resources_index = (self.current_object_resources_index + 1) % 3
            if event.key == pygame.K_MINUS:
                self.current_object_resources[self.current_object_resources_index] = 0
                self.current_object_resources_index = (self.current_object_resources_index + 1) % 3                
            if event.key == pygame.K_BACKSPACE:
                try: self.game_group.sprites()[-1].kill()
                except: pass
            if event.key == pygame.K_s:
                self.save(input("name> "))

        return super().take_input(inp, event)    

    def save(self, filename):
        data = []
        for obj in self.game_group.sprites():
            data.append({
                'type':obj.obj_type,
                'pos':tuple(obj.pos),
                'size':int(obj.size),
                'data':obj.data
            })
        json.dump(data, open("levels/%s.json" % filename, "w"))

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        text.render_multiline_to(self.game.screen, (3,3), self.current_object_type, "small", PICO_WHITE)
        text.render_multiline_to(self.game.screen, (3,16), str(self.current_object_resources[0]), "small", PICO_WHITE)
        text.render_multiline_to(self.game.screen, (18,16), str(self.current_object_resources[1]), "small", PICO_BLUE)
        text.render_multiline_to(self.game.screen, (33,16), str(self.current_object_resources[2]), "small", PICO_PINK)
        pygame.draw.rect(self.game.screen, PICO_LIGHTGRAY, (3 + self.current_object_resources_index * 15, 24,6,2))
        pygame.draw.rect(self.game.screen, PICO_WHITE, (*self.game.game_offset, *game.RES),1)
        return super().render()

    def update(self, dt):
        self.time += dt
        return super().update(dt)
