import pygame

import game
import levelscene
import rectangle
from aliens import alien
from button import Button
from colors import *
from elements import typewriter
from framesprite import FrameSprite
from resources import resource_path
from scene import Scene
from simplesprite import SimpleSprite
from states import Machine, UIEnabledState
from text import Text

V2 = pygame.math.Vector2

MOD_STRINGS = {
    'warp_drive':'Enemy starts with warp drive technology.',
    'big_planet':'Enemy starts with a super planet.',
    'reflector':'Enemy has planetary reflector shields.',
    'atomic_bomb':'Enemy has atomic bombs attached to their worker ships.',
    'ship_shield_far_from_home':'Enemy ships have a shield when attacking.',
    'battleship':'Enemy starts with a powerful ship.',
}

DIFFICULTY_VALUES = {
    1: [1,0,0],
    2: [1,1,1],
    3: [2,1,1],
    4: [2,2,2],
    5: [2,3,2],
    6: [3,3,3],
    7: [4,4,3],
    8: [0,0,0], # SHOP
    9: [5,5,3],
}

class LoadingScene(Scene):
    def __init__(self, game):
        super().__init__(game)
        self.rendered = False
        self.loaded = False
        self.levelscene = None
        self.loading_text = None
        self.warnings = []

    def start(self):
        self.group = pygame.sprite.LayeredDirty()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        
        self.time = 0

        galaxy = self.game.run_info.get_current_level_galaxy()
        self.galaxy = galaxy
        alien_code = galaxy['alien']
        alien_obj = alien.ALIENS[alien_code]
        self.nametext = typewriter.Typewriter(alien_obj.title, "huge", V2(50, 31) + self.game.game_offset, multiline_width=500, center=False, time_offset = -1)
        self.group.add(self.nametext)
        self.group.add(typewriter.Typewriter("ALIEN FORCES", "big", V2(50, 15) + self.game.game_offset, PICO_LIGHTGRAY, multiline_width=300, center=False))
        self.loading_text = Text("Loading...", "small", V2(game.RES[0] - 70, 326) + self.game.game_offset, center=False)
        self.loading_text.offset = (0.5, 0)
        self.loading_text.visible = False
        self.group.add(self.loading_text)

        self.portrait = SimpleSprite(V2(50, 65) + self.game.game_offset, "assets/%sgraphic.png" % alien_code)
        pygame.draw.rect(self.portrait.image, PICO_BLACK, (0,0,self.portrait.width, self.portrait.height), 1)
        self.group.add(self.portrait)
        self.portrait.pos = (0,-1000)
        #self.portrait.visible = False

        self.tips = []
        self.quote = None

        difficulty_width = 150
        difficulty_pos = V2(game.RES[0] / 2 - difficulty_width / 2, 175) + self.game.game_offset

        if galaxy['difficulty'] > 1:
            difficulty_pos = V2(game.RES[0] * 0.3 - difficulty_width / 2, 215) + self.game.game_offset       

        labels = ['Mining Rate', 'Attack Power', 'Tech Level']
        images = ['econ', 'attack', 'tech']
        elements = []
        for i in range(3):
            pos = difficulty_pos + V2(0, i * 20)
            t = Text(labels[i], "small", pos + V2(60, 0), PICO_ORANGE)
            t.offset = (1,0)
            self.group.add(t)
            t.visible = False
            elements.append(t)
            maxelem = 5
            if i == 2: maxelem = 3
            for z in range(maxelem):
                f = FrameSprite(pos + V2(70 + z * 14, -3), "assets/enemystrength-%s.png" % images[i], 11)
                if z >= DIFFICULTY_VALUES[galaxy['difficulty']][i]:
                    f.frame = 1
                else:
                    f.frame = 0
                self.group.add(f)
                f.visible = False
                elements.append(f)

        self.tips.append(elements)

        if galaxy['difficulty'] > 1:
            tw = 150
            if galaxy['difficulty'] < 4: i = 0
            elif galaxy['difficulty'] < 6: i = 1
            else: i = 2
            tip = alien_obj.tips[i]
            x = game.RES[0] * 0.7
            img = pygame.image.load(resource_path(tip[0]))
            s = SimpleSprite(V2(x, 165) + self.game.game_offset, img)
            s.offset = (0.5, 0)
            self.group.add(s)
            t = Text(tip[1], "small", V2(x - tw / 2, 240) + self.game.game_offset, multiline_width=tw, center=False)
            self.group.add(t)
            s.visible = False
            t.visible = False
            r = rectangle.Rectangle(V2(x - tw / 2, 169) + self.game.game_offset, (19, 11), PICO_YELLOW)
            t2 = Text("TIP", "small", V2(x - tw / 2 + 2, 171) + self.game.game_offset, PICO_BLACK)
            r.visible = False
            t2.visible = False
            self.group.add(r)
            self.group.add(t2)
            self.tips.append((r, t2))
            self.tips.append((s, t))
        else:
            self.quote = Text(alien_obj.get_quote(), "pixolde", V2(game.RES[0] / 2, 270) + self.game.game_offset, PICO_YELLOW, multiline_width=400)
            self.quote.offset = (0.5, 0)
            self.group.add(self.quote)
            self.quote.visible = False


        if galaxy['mods']:
            self.group.add(SimpleSprite(V2(61, 322) + self.game.game_offset, "assets/exclamation.png"))
            self.group.add(Text("DANGER", "small", V2(79, 320) + self.game.game_offset, PICO_YELLOW, multiline_width=400, center=False))
            self.group.add(Text(MOD_STRINGS[galaxy['mods'][0]], "small", V2(79, 330) + self.game.game_offset, PICO_WHITE, multiline_width=400, center=False))
            self.warnings = self.group.sprites()[-3:]
            for warning in self.warnings:
                warning.visible = False

        self.sm = Machine(UIEnabledState(self))

    def update(self, dt):
        for spr in self.group.sprites():
            spr.update(dt)
        self.time += dt
        if self.time > 1.5:
            self.portrait.pos = V2(50, 65) + self.game.game_offset
        if self.time > 1.5:
            self.loading_text.visible = True
        for i,tip in enumerate(self.tips):
            if self.time > 2.15 + i * 0.35:
                for z in tip:
                    z.visible = True
        if self.quote and self.time > 2.5:
            self.quote.visible = True
            
        if self.time > 3.25:
            for warning in self.warnings:
                warning.visible = True

        if not self.loaded and self.rendered and self.time > 4:
            self.levelscene = levelscene.LevelScene(
                self.game,
                self.galaxy['level'],
                self.galaxy['alien'],
                self.galaxy['difficulty'],
                self.galaxy['difficulty'],
                self.galaxy['name'],
                self.galaxy['description']
                )
            self.levelscene.start()
            self.loaded = True
            t = "Start"
            if self.game.input_mode == "joystick":
                t = "[*x*] Start"
            b = Button(V2(game.RES[0] - 80, 320) + self.game.game_offset, t, "big", self.on_click_start)
            b.offset = (0.5, 0)
            self.start_button = b
            self.ui_group.add(b)
            self.loading_text.kill()
        return super().update(dt)

    def on_click_start(self):
        self.game.scene = self.levelscene

    def take_input(self, inp, event):
        if inp == "confirm" and self.loaded:
            self.start_button.onclick()
        return super().take_input(inp, event)

    def render(self):
        self.game.screen.fill(PICO_DARKBLUE)
        self.group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        self.rendered = True 
        galaxy = self.game.run_info.get_current_level_galaxy()
