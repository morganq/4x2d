import pygame

import game
import menubackground
from colors import *
from helper import clamp
from scene import Scene
from simplesprite import SimpleSprite
from v2 import V2


class PlanetGenScene(Scene):
    def start(self):
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.bg = menubackground.MenuBackground(V2(0,0))
        self.background_group.add(self.bg)     
        self.debug_density = 0
        self.brush_radius = 3
        self.brush_pull = 0.5
        self.brush_strength = 0.5
        self.drag_pts = []
        self.mouse_pos = V2(0,0)

    def update(self, dt):
        self.bg.update(dt)
        return super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        #self.game.screen.blit(self.bg.particle_surface, (0,0))
        if self.debug_density > 0:
            self.debug_bg_render()
        self.game.screen.blit(self.bg.wobble_image, (0,0))
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)

        radius = (self.bg.field_to_screen(V2(self.brush_radius, 0)) - self.bg.field_to_screen(V2(0, 0))).x
        pygame.draw.circle(self.game.screen, PICO_GREEN, self.mouse_pos.tuple_int(), radius, max(round(self.brush_strength * 4),1))
        if self.brush_pull > 0:
            pygame.draw.circle(self.game.screen, PICO_GREEN, self.mouse_pos.tuple_int(), round(self.brush_pull * 4), 0)
        else:
            pygame.draw.circle(self.game.screen, PICO_PINK, self.mouse_pos.tuple_int(), round(-self.brush_pull * 4), 0)

        return super().render()

    def debug_bg_render(self):
        for y,row in enumerate(self.bg.motion_field):
            for x,col in enumerate(row):
                if (x % self.debug_density) == 0 and (y % self.debug_density) == 0:
                    pos = self.bg.field_to_screen(V2(x,y))

                    # Motion field
                    value = self.bg.motion_field[y][x]
                    p2 = pos + value * 3
                    pygame.draw.circle(self.game.screen, PICO_DARKGREEN, pos.tuple_int(), 1)
                    pygame.draw.line(self.game.screen, PICO_GREEN, pos.tuple_int(), p2.tuple_int())


    def take_input(self, inp, event):
        if inp == "mouse_drag":
            fpos = self.bg.screen_to_field_float(event.gpos)
            if self.drag_pts and (self.drag_pts[0] - event.gpos).sqr_magnitude() > 8 ** 2:
                last_fpos = self.bg.screen_to_field_float(self.drag_pts[0])
                self.bg.motion_draw(last_fpos, fpos, self.brush_radius, self.brush_strength, self.brush_pull)
                self.drag_pts = self.drag_pts[:-50]
            
            if not self.drag_pts or (self.drag_pts[-1] - event.gpos).sqr_magnitude() > 1 ** 2:
                self.drag_pts.append(event.gpos)

            self.mouse_pos = event.gpos
        
        if inp == "click":
            fpos = self.bg.screen_to_field_float(event.gpos)
            self.bg.motion_draw(fpos, fpos, self.brush_radius, self.brush_strength, self.brush_pull)

        if inp == "mouse_move":
            self.mouse_pos = event.gpos
        
        if inp == "unclick":
            self.drag_pts = []

        if inp == "action":
            img = self.bg.generate()
            
        if inp == "other":
            if event.key == pygame.K_0: self.debug_density = 0
            if event.key == pygame.K_1: self.debug_density = 1
            if event.key == pygame.K_2: self.debug_density = 2
            if event.key == pygame.K_3: self.debug_density = 3
            if event.key == pygame.K_4: self.debug_density = 4

            if event.key == pygame.K_COMMA: self.brush_pull = clamp(self.brush_pull - 0.125, -1, 1)
            if event.key == pygame.K_PERIOD: self.brush_pull = clamp(self.brush_pull + 0.125, -1, 1)
            if event.key == pygame.K_LEFTBRACKET: self.brush_strength = clamp(self.brush_strength - 0.125, 0.125, 1)
            if event.key == pygame.K_RIGHTBRACKET: self.brush_strength = clamp(self.brush_strength + 0.125, 0.125, 1)

            if event.key == pygame.K_f:
                img = self.bg.generate(False)
            if event.key == pygame.K_s:
                self.bg.save()
            if event.key == pygame.K_c:
                print(self.bg.chosen_colors)


        if inp == "up": self.brush_radius = clamp(self.brush_radius + 1, 1, 20)
        if inp == "down": self.brush_radius = clamp(self.brush_radius - 1, 1, 20)

        return super().take_input(inp, event)
