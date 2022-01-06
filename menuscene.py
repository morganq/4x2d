import math
import random
import sys

import pygame

import button
import controlsscene
import creditsscene
import explosion
import framesprite
import game
import hqlogo
import joyresolver
import menu
import menubackground
import newgamescene
import save
import scene
import simplesprite
import sound
import states
import text
import tooltippanel
import tutorial.introscene
from colors import *
from helper import clamp
from particle import Particle
from run import RunInfo
from slider import Slider
from spritebase import SpriteBase
from starmap import starmapscene
from v2 import V2


class ModsUIState(states.UIEnabledState):
    is_basic_joystick_panel = True
    def __init__(self, scene):
        super().__init__(scene)

    def get_joystick_cursor_controls(self):
        return self.scene.mods_controls

    def take_input(self, input, event):
        if input == "confirm":
            pass
        return super().take_input(input, event)

class ModifierButton(framesprite.FrameSprite, tooltippanel.Tooltippable):
    def __init__(self, name, pos, sprite_sheet=None, onclick=None, tooltip_title=None, tooltip_body=None):
        self.name = name
        super().__init__(pos, sprite_sheet=sprite_sheet, frame_width=31)
        tooltippanel.Tooltippable.setup(self, tooltip_title, tooltip_body)
        self.onclick = onclick
        self.on("mouse_down", self.onclick)
        self.selectable = True
        self.set_state("locked")

    def set_state(self, name):
        self.state = name
        if self.state == "locked": self.frame = 2
        elif self.state == "disabled": self.frame = 1
        else: self.frame = 0

class Parallaxed:
    def __init__(self, obj, degree):
        self.obj = obj
        self.degree = degree
        self.end_pos = self.obj.pos

    def update(self, time):
        t = clamp(time / 2.5, 0, 1)
        tz = (math.cos(t * 3.14159) * -0.5 + 0.5) ** 0.5
        delta = V2(0, 300) * self.degree * (1-tz)
        self.obj.pos = self.end_pos + delta


class MainMenuOption(framesprite.FrameSprite):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(pos, sprite_sheet=sprite_sheet, frame_width=frame_width)
        self.scene = scene
        self.label = None
        self.initial_pos = pos
        self.hover = False
        self.onclick_callback = onclick
        self.selectable = True
        self.on("mouse_down", lambda *args:self.onclick())
        self.on("mouse_enter", self.mouse_enter)
        self.on("mouse_exit", self.mouse_exit)

    def onclick(self):
        sound.play("click1")
        self.onclick_callback()

    def mouse_enter(self, *args):
        self.label._generate_image(True)
        self.hover = True

    def mouse_exit(self, *args):
        self.label._generate_image(False)
        self.hover = False

class IntelOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.scene.time < 6:
            return
        if self.hover:
            self.hover_time += dt        
            self.frame = int((self.hover_time * 3.5) % 5) + 5
        else:
            self.frame = 4
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)

class MultiplayerOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.hover:
            self.hover_time += dt        
            self.frame = min(int((self.hover_time * 6.5) % 8), 5)
        else:
            self.frame = 0
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)        

class ContinueOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.hover:
            self.hover_time += dt        
            self.frame = int((self.hover_time * 12) % 6)
        else:
            self.frame = 0
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)

class NewGameOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.hover:
            self.hover_time += dt
            self.pos = self.initial_pos + V2(4, -1.5) * math.sin(self.hover_time * 3.14159)
            # Make an explosion for the thruster, with a random chance.

            if random.random() < 0.25:
                def scale_fn(t):
                    return 1 - t
                    #return math.sin(t * 3.14159)

                offset = V2(16,15)
                if random.random() > 0.5:
                    offset = V2(18,27)
                ep = self.pos + offset + V2.random_angle() * 0
                vel = V2(-30, 4)
                e = explosion.Explosion(ep, [PICO_WHITE, PICO_YELLOW, PICO_ORANGE, PICO_RED], 1, random.randint(3,6), scale_fn, velocity=vel)
                self.scene.game_group.add(e)
        else:
            self.pos = self.initial_pos
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)

class OptionsOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.hover:
            self.hover_time += dt
            self.pos = self.initial_pos + (
                V2(4, 0) * math.sin(self.hover_time * 1.25) +
                V2(0, 4) * math.cos(self.hover_time * 1.25)
            )
            if random.random() < 0.25:
                colors = [PICO_WHITE, PICO_BLUE, PICO_BLUE]
                if random.random() < 0.5:
                    colors = [PICO_WHITE, PICO_YELLOW, PICO_YELLOW]
                p = Particle(
                    colors,
                    1,
                    self.pos + V2(41,11) + V2.random_angle() * 1,
                    0.25,
                    V2.random_angle() * 20
                )
                self.scene.game_group.add(p)

            if random.random() < 0.25:
                ep = self.pos + V2(19,45)
                def scale_fn(t): return 1 - t
                e = explosion.Explosion(
                    ep,
                    [PICO_WHITE, PICO_LIGHTGRAY, PICO_WHITE, PICO_LIGHTGRAY],
                    1,
                    random.randint(3,6),
                    scale_fn,
                    velocity=V2(0,9) + V2.random_angle() * 4
                )
                e.layer = -1
                self.scene.game_group.add(e)                

        else:
            self.pos = self.initial_pos
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)

class ExitOption(MainMenuOption):
    def __init__(self, scene, pos, sprite_sheet=None, frame_width=None, onclick=None):
        super().__init__(scene, pos, sprite_sheet=sprite_sheet, frame_width=frame_width, onclick=onclick)
        self.hover_time = 0

    def update(self, dt):
        if self.hover:
            self.hover_time += dt
            self.pos = self.initial_pos + V2(1, -3) * math.sin(self.hover_time * 6)
            # Make an explosion for the thruster, with a random chance.

            if random.random() < 0.25:
                def scale_fn(t):
                    return 1 - t
                    #return math.sin(t * 3.14159)

                offset = V2(2,29)
                if random.random() > 0.5:
                    offset = V2(12,32)
                ep = self.pos + offset + V2.random_angle() * 0
                vel = V2(-7, 20)
                e = explosion.Explosion(ep, [PICO_WHITE, PICO_YELLOW, PICO_ORANGE, PICO_RED], 1, random.randint(2,3), scale_fn, velocity=vel)
                self.scene.game_group.add(e)
        else:
            self.pos = self.initial_pos
        return super().update(dt)

    def mouse_enter(self, *args):
        self.hover_time = 0
        return super().mouse_enter(*args)        

class MenuOptionLabel(SpriteBase):
    def __init__(self, pos, option_pos, label):
        super().__init__(pos)
        self.option_pos = option_pos
        self.label = label
        self._generate_image()
        self.visible = False

    def _generate_image(self, hover=False):
        padding = 4
        delta = self.option_pos - self.pos
        is_left = delta.x > 0
        is_top = delta.y > 0
        lsurf = text.render_multiline(self.label, "small", PICO_WHITE)
        self._width = lsurf.get_width() + abs(delta.x) + padding
        self._height = lsurf.get_height() + abs(delta.y) + padding
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        # X and Y position to place the text
        if is_left: x = padding
        else: x = self._width - lsurf.get_width() - padding
        if is_top: y = padding
        else: y = self._height - lsurf.get_height() - padding
        if hover:
            pygame.draw.rect(self.image, PICO_BLUE, (x-2,y-1, lsurf.get_width() + 4, 10), 0)
        self.image.blit(lsurf, (x,y))

        # Figure out the points for the label line
        if is_left:
            p1x = x + lsurf.get_width() + 2
            p1y = y + 4
        else:
            p1x = x - 3
            p1y = y + 3

        if is_left: p2x = self._width - padding
        else: p2x = padding
        if is_top: p2y = self._height - padding
        else: p2y = padding

        sdx = 1 if delta.x >= 0 else -1
        sdy = 1 if delta.y >= 0 else -1

        p3x = p2x + (abs(p2y-p1y)) * -sdx
        p3y = p1y

        pygame.draw.line(self.image, PICO_BLUE, (p1x, p1y), (p3x, p3y), 1)
        pygame.draw.line(self.image, PICO_BLUE, (p3x, p3y), (p2x, p2y), 1)
        pygame.draw.line(self.image, PICO_BLUE, (p1x, p1y - 4), (p1x, p1y + 4), 1)

        self._recalc_rect()

MODE_START = "start"
MODE_TAKEOFF = "takeoff"
MODE_MODS = "mods"

class MenuScene(scene.Scene):
    def take_raw_input(self, event):
        self.game.input_mode = game.Game.INPUT_MOUSE

    def start(self):
        self.joy = joyresolver.JoyResolver(self.on_joy_press)
        self.set_starting_button = False
        self.background_group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.parallax = []
        self.stars = []

        self.choices = []
        self.current_choice = 2
        self.using_joy = True
        self.mode = MODE_START
        self.takeoff_time = 0

        self.run_challenges = []
        self.run_modifiers = []
        
        minx = -200
        miny = -200
        maxx = self.game.game_resolution.x + 200
        maxy = self.game.game_resolution.y + 200
        for i in range(320):
            s = framesprite.FrameSprite(V2(random.randint(minx, maxx),random.randint(miny, maxy)), "assets/bgstar.png", 11)
            s.frame = 4 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.05))
            self.stars.append(s)
        for i in range(90):
            s = framesprite.FrameSprite(V2(random.randint(minx, maxx),random.randint(miny, maxy)), "assets/bgstar.png", 11)
            s.frame = 2 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.1))   
            self.stars.append(s)         
        for i in range(40):
            s = framesprite.FrameSprite(V2(random.randint(minx, maxx),random.randint(miny, maxy)), "assets/bgstar.png", 11)
            s.frame = 0 + random.randint(0,1)
            self.background_group.add(s)
            self.parallax.append(Parallaxed(s, 0.2)) 
            self.stars.append(s)           

        earth_pos = self.game.game_offset + V2(120, 140)
        self.bg_earth = simplesprite.SimpleSprite(earth_pos, "assets/title-earth.png")
        self.game_group.add(self.bg_earth)
        self.parallax.append(Parallaxed(self.bg_earth, 1))

        self.bg_enemies = IntelOption(self, earth_pos + V2(-165, 7), "assets/title-enemies.png", 251, onclick=self.click_intel)
        self.game_group.add(self.bg_enemies)
        self.bg_enemies.visible = False
        self.choices.append(self.bg_enemies)
        
        res = self.game.game_resolution

        self.bg_multiplayer = MultiplayerOption(self, V2(res.x * 0.2, res.y / 8), "assets/title-multiplayer.png", 58, onclick=self.click_multiplayer)
        self.parallax.append(Parallaxed(self.bg_multiplayer, 0.15))
        self.game_group.add(self.bg_multiplayer)
        self.choices.append(self.bg_multiplayer)
        self.bg_multiplayer.visible = False

        self.bg_continue = None
        if self.game.run_info.started:
            self.bg_continue = ContinueOption(self, V2(res.x * 0.4, res.y / 8), "assets/title-continue.png", frame_width=109, onclick=self.click_continue)
            self.parallax.append(Parallaxed(self.bg_continue, 0.05))
            self.game_group.add(self.bg_continue)
            self.choices.append(self.bg_continue)

        self.bg_newgame_path = simplesprite.SimpleSprite(earth_pos + V2(150, -32), "assets/title-newgame-path.png")
        self.bg_newgame_path.visible = False
        self.game_group.add(self.bg_newgame_path)        

        self.bg_newgame = NewGameOption(self, earth_pos + V2(265, -39), "assets/title-newgame-ship.png", onclick=self.click_new)
        self.bg_newgame.visible = False
        self.game_group.add(self.bg_newgame)
        self.choices.append(self.bg_newgame)

        self.bg_options = OptionsOption(self, V2(res.x * 3 / 4, res.y * 0.55), "assets/title-options.png", onclick=self.click_options)
        self.parallax.append(Parallaxed(self.bg_options, 1.5))
        self.game_group.add(self.bg_options)                        
        self.choices.append(self.bg_options)
        self.bg_options.visible = False

        self.bg_exit = ExitOption(self, V2(res.x * 0.7, res.y * 0.8), "assets/title-exit.png", onclick=sys.exit)
        self.parallax.append(Parallaxed(self.bg_exit, 5))
        self.game_group.add(self.bg_exit)        
        self.choices.append(self.bg_exit)
        self.bg_exit.visible = False

        self.logo = hqlogo.HQLogo(earth_pos + V2(89, 103), delay=6.25)
        self.logo.offset = (0.5, 0.5)
        self.game_group.add(self.logo)

        l = MenuOptionLabel(self.bg_enemies.pos + V2(78,-2) + V2(22,-6) + V2(-4,-4), self.bg_enemies.pos + V2(78,-2) + V2(-4,-4), "Intel")
        self.bg_enemies.label = l
        self.ui_group.add(l)

        l = MenuOptionLabel(self.bg_multiplayer.pos + V2(-28,-2) + V2(-22,-6) + V2(-4,-4), self.bg_multiplayer.pos + V2(-28,-2) + V2(-4,-4), "Multiplayer")
        self.bg_multiplayer.label = l
        self.ui_group.add(l)  

        if self.bg_continue:
            l = MenuOptionLabel(self.bg_continue.pos + V2(18,22) + V2(42,-24) + V2(-4,-4), self.bg_continue.pos + V2(18,22) + V2(-4,-4), "Continue")
            self.bg_continue.label = l
            self.ui_group.add(l)              

        l = MenuOptionLabel(self.bg_newgame.pos + V2(38,26) + V2(22,6) + V2(-4,-4), self.bg_newgame.pos + V2(38,26) + V2(-4,-4), "New Game")
        self.bg_newgame.label = l
        self.ui_group.add(l)        

        l = MenuOptionLabel(self.bg_options.pos + V2(-30,2) + V2(-22,-3) + V2(-4,-4), self.bg_options.pos + V2(-30,2) + V2(-4,-4), "Options")
        self.bg_options.label = l
        self.ui_group.add(l)

        l = MenuOptionLabel(self.bg_exit.pos + V2(9,16) + V2(22,1) + V2(-4,-4), self.bg_exit.pos + V2(9,16) + V2(-4,-4), "Exit")
        self.bg_exit.label = l
        self.ui_group.add(l)         

        x = 340 * (self.game.game_resolution.x / game.RES[0])
        y = self.game.game_resolution.y / 2 - 50

        if self.game.first_load:
            self.game.first_load = False
            self.time = 0
        else:
            self.skip_intro()

        self.sm = states.Machine(states.UIEnabledState(self))

    def skip_intro(self):
        self.time = 8
        self.logo.time = 8
        self.logo._generate_image()        

    def on_joy_press(self, dir):
        self.using_joy = True
        self.choices[self.current_choice].mouse_exit()
        if dir in ['right', 'down']:
            self.current_choice = min(self.current_choice + 1, len(self.choices) - 1)
        if dir in ['up', 'left']:
            self.current_choice = max(self.current_choice - 1, 0)
        self.choices[self.current_choice].mouse_enter()

    def update(self, dt):
        self.time += min(dt,0.1)
        if self.mode == MODE_TAKEOFF:
            self.takeoff_update(dt)
        elif self.mode == MODE_MODS:
            self.mods_update(dt)
        else:
            self.basic_update(dt)

        for para in self.parallax:
            para.update(self.time)

        for spr in self.game_group.sprites():
            spr.update(dt)

        for spr in self.ui_group.sprites():
            spr.update(dt)            

        for i in range(10):
            s = random.choice(self.stars)
            s.frame = int(s.frame / 2) * 2 + random.randint(0,1)

        super().update(dt)

    def basic_update(self, dt):
        # Enemies
        off = 0.25
        if self.time > 5.5 + off:
            self.bg_newgame_path.visible = True
            self.bg_newgame.visible = True
            self.bg_enemies.frame = 4
        if self.time > 9 + off:
            for i, o in enumerate([self.bg_enemies, self.bg_multiplayer, self.bg_options, self.bg_exit]):
                o.visible = True
        elif self.time > 4.25 + off:
            self.bg_enemies.frame = 4
        elif self.time > 4.0 + off:
            self.bg_enemies.frame = 3
        elif self.time > 3.7 + off:
            self.bg_enemies.frame = 2
        elif self.time > 3.25 + off:
            self.bg_enemies.frame = 1
        elif self.time > 3 + off:
            self.bg_enemies.visible = True

        if self.time > 10 and not self.set_starting_button:
            self.set_starting_button = True
            self.choices[self.current_choice].mouse_enter()

        labels = [self.bg_enemies.label, self.bg_multiplayer.label, self.bg_newgame.label, self.bg_options.label, self.bg_exit.label]
        if self.bg_continue:
            labels.insert(2, self.bg_continue.label)
        i = clamp(int((self.time - 9.5) * 9), -1, len(labels))
        if i >= 0:
            for j in range(i):
                labels[j].visible = True
    
    def mods_update(self, dt):
        self.bg_newgame.hover = True

    def takeoff_update(self, dt):
        self.takeoff_time += dt
        for obj in [self.bg_enemies, self.bg_earth, self.bg_multiplayer, self.bg_continue, self.bg_options, self.bg_exit, self.bg_newgame_path]:
            if obj:
                obj.visible = False
                obj.hover = False
                if hasattr(obj, "label"):
                    obj.label.visible = False
        self.bg_newgame.label.visible = False
        self.bg_newgame.hover = True
        ow,oh = self.takeoff_earth.base_image.get_size()
        nw = int(ow / (self.takeoff_time * 3 + 1))
        nh = int(oh / (self.takeoff_time * 3 + 1))
        offx = 0.05
        offy = 0.8
        self.takeoff_earth.x = (ow - nw) * offx
        self.takeoff_earth.y = (oh - nh) * offy
        self.takeoff_earth.image = pygame.transform.scale(self.takeoff_earth.base_image, (nw,nh))

        ep = V2(self.game.game_resolution.x * (offx + 0.025), self.game.game_resolution.y * (offy + 0.025))
        for p in self.parallax:
            if p.degree <= 0.2:
                earth_delta = p.end_pos - ep
                p.end_pos += V2(-30 * dt * p.degree, 0) - earth_delta * p.degree * dt * 0.3
                #p.obj.x -= dt * p.degree * 10
        if self.takeoff_time >= 2.5:
            if self.game.save.victories > 0:
                self.mode = MODE_MODS
                self.create_mods_ui()
                self.sm.transition(ModsUIState(self))
            else:
                self.click_continue_to_mission()

    def create_mods_ui(self):
        self.mods_controls = []
        TITLES = {
            'fragile_planets':'Fragility',
            'low_range':'Fuel Crisis',
            'worker_loss':'Perilous Frontier',
            'low_oxygen':'Oxygen Leak',
            'small_army':'Skeleton Crew',
            'terraform':'Barysi Terraform',
            'hacking':'Network Hack',
            'void':'Void Beacon',
            'timeloop':'Time Loop',
        }
        BODIES = {
            'fragile_planets':'Your planets have [!-75% health]. [^+10% Score]',
            'low_range':'All ships have [!limited fuel]. [Fighters] have [!-35% fuel]. [^+10% Score]',
            'worker_loss':'Worker ships [!lose 1 population] when launched. [^+10% Score]',
            'low_oxygen':'Start with [!-50% Oxygen]. [^+10% Score]',
            'small_army':'Maximum army size is [!10]. [^+10% Score]',
            'terraform':'Capturing a planet converts [^30%] of its [Iron] to [Ice] or [Gas]. Requires [!+1 challenge]',
            'hacking':'33% chance to [^gain control] of an enemy ship if you destroy it in deep space. Requires [!+1 challenge]',
            'void':'Your planets eminate a [^Void Field]. Requires [!+1 challenge]',
            'timeloop':'In each sector, +3 random planets are time looped. Requires [!+2 challenges]',
        }
        REQS = {
            'fragile_planets':1,
            'low_range':2,
            'worker_loss':4,
            'low_oxygen':6,
            'small_army':10,
            'terraform':1,
            'hacking':3,
            'void':7,
            'timeloop':15
        }

        x1 = self.game.game_resolution.x / 2 - (((31 * 5) + (4 * 4)) / 2)
        y1 = self.game.game_resolution.y / 2

        bg = simplesprite.SimpleSprite(V2(x1, y1), "assets/mods_bg.png")
        self.ui_group.add(bg)

        ct1 = text.Text("Modifiers", "small", V2(x1 - 10, y1 + 9), multiline_width=100)
        ct1.offset = (1,0)
        self.ui_group.add(ct1)
        self.modifiers_info = text.Text("0", "small", V2(x1 - 10, y1 + 20), PICO_GREEN, multiline_width=100)
        self.modifiers_info.offset = (1,0)
        self.ui_group.add(self.modifiers_info)

        ct2 = text.Text("Challenges", "small", V2(x1 - 10, y1 + 63), multiline_width=100)
        ct2.offset = (1,0)
        self.ui_group.add(ct2)
        self.challenges_info = text.Text("0/0", "small", V2(x1 - 10, y1 + 74), PICO_GREEN, multiline_width=100)
        self.challenges_info.offset = (1,0)
        self.ui_group.add(self.challenges_info)

        self.negative_mods = []
        self.positive_mods = []

        for i,nm in enumerate(['fragile_planets', 'low_range', 'worker_loss', 'low_oxygen', 'small_army']):
            def make_onclick(nm):
                return lambda *args:self.click_challenge(nm, *args)
            x = x1 + i * 35 + 3
            y = y1 + 56
            title = "Locked"
            body = "Victories to unlock: %d" % REQS[nm]
            if self.game.save.victories >= REQS[nm]:
                title = TITLES[nm]
                body = BODIES[nm]                
            b = ModifierButton(nm, V2(x, y), "assets/mod_%s.png" % nm, make_onclick(nm), title, body)
            if self.game.save.victories >= REQS[nm]:
                b.set_state("disabled")
            self.ui_group.add(b)
            self.negative_mods.append(b)

        for i,nm in enumerate(['terraform', 'hacking', 'void', 'timeloop']):
            def make_onclick(nm):
                return lambda *args:self.click_modifier(nm, *args)
            x = x1 + i * 35 + 3
            y = y1 + 3
            title = "Locked"
            body = "Victories to unlock: %d" % REQS[nm]
            if self.game.save.victories >= REQS[nm]:
                title = TITLES[nm]
                body = BODIES[nm]                
            b = ModifierButton(nm, V2(x, y), "assets/mod_%s.png" % nm, make_onclick(nm), title, body)
            if self.game.save.victories >= REQS[nm]:
                b.set_state("disabled")
            self.ui_group.add(b)
            self.positive_mods.append(b)

        self.continue_button = button.Button(V2(self.game.game_resolution.x/2, y1 + 100), "Continue to mission", "small", self.click_continue_to_mission)
        self.continue_button.offset = (0.5, 0)
        self.ui_group.add(self.continue_button)
        self.mods_controls = [self.positive_mods, self.negative_mods, [self.continue_button]]

    def update_challenge_texts(self):
        have = len(self.run_challenges)
        reqd = self.get_required_challenges()
        if have < reqd:
            self.challenges_info.color = PICO_RED
        else:
            self.challenges_info.color = PICO_GREEN
        self.challenges_info.set_text("%d/%d" % (have, reqd))

        self.modifiers_info.set_text("%d" % len(self.run_modifiers))

    def get_required_challenges(self):
        MOD_REQS = {
            'terraform':1,
            'hacking':1,
            'void':1,
            'timeloop':2
        }
        total = 0
        for name in self.run_modifiers:
            total += MOD_REQS.get(name, 0)
        return total

    def update_continue_button(self):
        enabled = len(self.run_challenges) >= self.get_required_challenges()
        self.continue_button.disabled = not enabled
        if enabled:
            self.continue_button.text = "Continue to mission"
            self.continue_button.color = PICO_BLUE
            self.continue_button._generate_image()
        else:
            self.continue_button.text = "Need more challenges"
            self.continue_button.color = PICO_LIGHTGRAY
            self.continue_button._generate_image()

    def click_modifier(self, pm, btn, pos):
        if btn.state == "disabled":
            btn.set_state("enabled")
            self.run_modifiers.append(pm)
            self.run_modifiers = list(set(self.run_modifiers))
            self.update_challenge_texts()
            self.update_continue_button()
        elif btn.state == "enabled":
            btn.set_state("disabled")
            self.run_modifiers.remove(pm)
            self.run_modifiers = list(set(self.run_modifiers))            
            self.update_challenge_texts()
            self.update_continue_button()

    def click_challenge(self, nm, btn, pos):
        if btn.state == "disabled":
            btn.set_state("enabled")
            self.run_challenges.append(nm)
            self.run_challenges = list(set(self.run_challenges))
            self.update_challenge_texts()
            self.update_continue_button()
        elif btn.state == "enabled":
            btn.set_state("disabled")
            self.run_challenges.remove(nm)
            self.run_challenges = list(set(self.run_challenges))            
            self.update_challenge_texts()
            self.update_continue_button()

    def click_continue_to_mission(self, *args):
        self.game.scene = newgamescene.NewGameScene(self.game, self.run_challenges, self.run_modifiers)
        self.game.scene.start()

    def render(self):   
        self.game.screen.fill(PICO_BLACK)        
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        super().render()    

    def click_multiplayer(self):
        self.game.set_scene("multiplayer_menu")

    def click_tutorial(self):
        self.game.scene = tutorial.introscene.IntroScene(self.game)
        self.game.scene.start()

    def click_options(self):
        self.game.set_scene("options")

    def click_continue(self):
        self.game.run_info = self.game.save.get_run_state()
        self.game.scene = starmapscene.StarMapScene(self.game)
        self.game.scene.start()        

    def click_new(self):
        #self.game.scene = newgamescene.NewGameScene(self.game)
        #self.game.scene.start()
        self.takeoff_earth = simplesprite.SimpleSprite(V2(0,0))
        self.takeoff_earth.base_image = pygame.Surface(self.game.game_resolution.tuple(), pygame.SRCALPHA)
        self.takeoff_earth.base_image.blit(self.bg_earth.image, self.bg_earth.pos.tuple_int())
        self.takeoff_earth.base_image.blit(self.bg_enemies.image, self.bg_enemies.pos.tuple_int())
        self.takeoff_earth.image = self.takeoff_earth.base_image
        self.game_group.add(self.takeoff_earth)
        self.mode = MODE_TAKEOFF
        self.logo.kill()

    def click_intel(self):
        pass                    

    def take_input(self, inp, event):
        if self.mode == MODE_MODS:
            self.sm.state.take_input(inp, event)
        else:
            if self.time < 6:
                if inp == "menu":
                    self.skip_intro()
                return
            if inp == "joymotion":
                self.joy.take_input(inp, event)
                self.game.input_mode = "joystick"
            elif inp == "confirm":
                self.choices[self.current_choice].onclick()
                self.game.input_mode = "joystick"
            else:
                self.sm.state.take_input(inp, event)
            if inp == "mouse_move" and self.using_joy:
                self.game.input_mode = "mouse"
                self.choices[self.current_choice].mouse_exit()
                self.using_joy = False
        #return super().take_input(inp, event)
