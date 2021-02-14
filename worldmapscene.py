import scene
import pygame
import game
import simplesprite
import framesprite
import random
import text
import levelscene
import sound
import tilemap
from collections import defaultdict
from resources import resource_path

LEVELS = [
    ('intro1', 'SEATTLE', 'Docks', (94, 118), 16, 20, 30),
    ('intro2', 'SEATTLE', 'Industrial Center', (114, 127), 32, 33, 40),
    ('intro3', 'SEATTLE', 'City Square', (113, 88), 18, 25, 32), 
    ('intro4', 'SEATTLE', 'Park', (133, 87), 28, 35, 50), # good
    ('backandforth', 'SEATTLE', 'Train Station', (156, 116), 28, 30, 50), #e in depth than ^ good
    ('multidrop', 'SEATTLE', 'Sprawl', (180, 141), 29, 34, 40), # just mor

    ('intropolice', 'OAKLAND', 'Police Training', (55, 280), 10, 12, 15), 
    ('policemaneuver', 'OAKLAND', 'Patrol', (96, 281), 31, 34, 45),
    ('extrafacts', 'OAKLAND', 'Excess Capacity', (124, 300), 24, 30, 40), # no problem
    ('introturnaround', 'OAKLAND', 'Roundabout', (168, 335), 48, 52, 55),
    ('basicturnaround', 'OAKLAND', 'Tightly Packed', (215, 344), 19, 25, 35),
    
    ('simplepicker', 'SANTIAGO', 'Convergence', (40, 477), 28, 35, 50), # good
    ('harderpicker', 'SANTIAGO', 'Outskirts', (95, 488), 58, 62, 120), # good one
    ('policeline', 'SANTIAGO', 'Blue Line', (148, 541), 25, 30, 40), # I think good!
    ('policeavoid', 'SANTIAGO', 'Squad', (182, 510), 40, 45, 50), # subtle and important lesson
    ('introsoldier', 'SANTIAGO', 'Armed Forces', (202, 496), 29, 33, 36), # good

    ('multipolice', 'BARCELONA', 'Police HQ', (292, 286), 34, 44, 54), # not as tricky as it may look
    ('policeblock', 'BARCELONA', 'Shortcut', (327, 311), 22, 25, 32), # yep good
    ('intromultisoldier', 'BARCELONA', 'Barracks', (359, 291), 33, 40, 45), # easy 
    ('manyturnaround', 'BARCELONA', 'Barrio', (379, 320), 60, 65, 75), # 3-4
    ('diagonalroute', 'BARCELONA', 'Hillside', (384, 353), 55, 60, 75), # 4

    ('awkwardsoldier', 'ALGIERS', 'Recruits', (294, 509), 50, 55, 65), # 4 - maybe slightly too hard?
    ('hardturnaround', 'ALGIERS', 'Alleyway', (339, 482), 43, 50, 70), # probably a bit hard
    ('policemultihall', 'ALGIERS', 'Kettle', (380, 513), 45, 50, 55), #kinda hard
    ('complexmultisoldier', 'ALGIERS', 'Infiltration', (405, 488), 67, 75, 85), # 5
    ('coplocks', 'ALGIERS', 'Tactical', (447, 480), 51, 58, 65), # 5

    ('coplock2', 'MINSK', 'Lockdown', (324, 105), 50, 55, 65), # 5
    ('introtower', 'MINSK', 'Cell Tower', (361, 122), 15, 20, 25), # good
    ('tower2', 'MINSK', 'Dead End', (400, 111), 23, 25, 35), # good
    ('rearrangesoldiers', 'MINSK', 'Operations', (460, 143), 30, 40, 50), # good    

    ('push2copsaround', 'TEHRAN', 'Standoff', (548, 93), 85, 95, 105), # 5
    ('pods', 'TEHRAN', 'Campus', (602, 130), 58, 70, 85), # 5
    ('dividesoldiers', 'TEHRAN', 'Palace', (662, 90), 100, 110, 130), # 5
    ('complex2', 'TEHRAN', 'Density', (693, 125), 50, 100, 120), # 5

    ('towerring', 'MUMBAI', 'Ring', (590, 288), 55, 65, 70), # 5-6
    ('hardsoldierpolice', 'MUMBAI', 'Parade', (615, 324), 70, 80, 90), # 6
    ('breakupcops', 'MUMBAI', 'Commercial District', (662, 319), 60, 65, 80), # good - 6
    ('complex1', 'MUMBAI', 'Fortification', (711, 346), 93, 110, 130),  # 7
    
    ('tonsofcops', 'HONG KONG', 'Police Riot', (567, 532), 50, 60, 70), # 8
    ('twotowercomplex', 'HONG KONG', 'Interference', (626, 479), 50, 60, 70), # 7
    ('twotowers', 'HONG KONG', 'Comms Center', (674, 477), 35, 42, 50),  # great - 7
    ('towercomplex', 'HONG KONG', 'Hostile Dispatch', (691, 537), 50, 60, 70), # 7

    ('tank1', 'NEW YORK CITY', 'Big Gun', (823, 292), 40, 50, 60),
    ('tank2', 'NEW YORK CITY', 'Friendly Fire', (840, 329), 30, 45, 60),
    ('tank3', 'NEW YORK CITY', 'Artillery', (898, 287), 40, 55, 65),
    ('tank4', 'NEW YORK CITY', 'Martial Law', (919, 339), 50, 100, 120),
    ('tank5', 'NEW YORK CITY', 'Smashing Obstacles', (977, 293), 90, 110, 130),
]
# SEATTLE, OAKLAND, SANTIAGO, BARCELONA, ALGIERS, MINSK, TEHRAN, MUMBAI, HONG KONG, NEW YORK CITY

SCROLLS = {
    'SEATTLE': (11,9),
    'OAKLAND': (11,204),
    'SANTIAGO': (10,401),
    'BARCELONA': (262,205),
    'ALGIERS': (262,401),
    'MINSK': (262,9),
    'TEHRAN': (513,9),
    'MUMBAI': (513,204),
    'HONG KONG': (513,401),
    'NEW YORK CITY': (766,204)
}
CITIES = list(SCROLLS.keys())

class WorldMapScene(scene.Scene):
    def __init__(self, game, level_index):
        scene.Scene.__init__(self, game)
        self.starting_level_index = level_index or 0
        self.animated = []
        self.animation_timer = 0

    def start(self):
        self.scroll = (0,0)
        self.back_group = pygame.sprite.Group()
        self.fore_group = pygame.sprite.Group()
        self.levelobjs = []
        self.map = simplesprite.SimpleSprite("assets/worldmaplayout.png", (0,0))
        self.back_group.add(self.map)

        for i,level in enumerate(LEVELS):
            x,y = level[3][0], level[3][1]
            obj = framesprite.FrameSprite("assets/mapflag copy.png", 12)
            if self.game.save.get_level_state(i)['beaten']:
                obj.set_frame(1)
            obj.move(x - 6,y - 10)
            self.levelobjs.append((obj, level))
            self.back_group.add(obj)

        self.popup_sprites = []

        self.arrow = framesprite.FrameSprite("assets/selectarrow.png", 11)
        self.arrow.move(-11, -11)
        self.animated.append(self.arrow)
        self.fore_group.add(self.arrow)

        self.next_text = text.Text(">", "small", (0,-20))
        self.prev_text = text.Text("<", "small", (0,-20))
        self.fore_group.add(self.next_text)
        self.fore_group.add(self.prev_text)

        overlay = simplesprite.SimpleSprite("assets/mapoverlay.png", (0,0))
        self.fore_group.add(overlay)
        self.selected_level = self.starting_level_index
        self.update_selection()
        self.flash_index = 0
        sound.play_music('overworld')

    def render(self):
        self.game.screen.fill(game.BGCOLOR)
        scrollsurf = pygame.Surface(self.map.image.get_size())
        self.back_group.draw(scrollsurf)
        self.game.screen.blit(scrollsurf, (-self.scroll[0], -self.scroll[1]))
        self.fore_group.draw(self.game.screen)

    def update_selection(self):
        (lvl, name1, name2, pos, *extras) = LEVELS[self.selected_level]
        name2 = "%d - %s" % (self.selected_level + 1, name2)
        self.scroll = SCROLLS[name1]
        self.arrow.move(pos[0] - self.scroll[0] -13, pos[1] - self.scroll[1] - 18)

        self.back_group.remove(self.popup_sprites)
        self.popup_sprites = []
        
        y = self.scroll[1] + 10
        w,h = (text.FONTS['big'].get_rect(name1)[2] + 12, 50)
        w2 = text.FONTS['small'].get_rect(name2)[2] + 12
        w = max(w, w2, 120)
        fw = w + 43
        x = self.scroll[0] + 120 - fw / 2
        city = text.Text(name1, "big", (x + 5, y + 5), color=(game.BGCOLOR), border=False)
        background = pygame.sprite.Sprite()
        
        background.image = pygame.Surface((fw,h))
        background.rect = (x, y, background.image.get_size()[0] + 10, background.image.get_size()[1])
        background.image.fill(game.FGCOLOR)
        pygame.draw.rect(background.image, game.FGCOLOR, (0, 0, w, h))
        pygame.draw.rect(background.image, game.BGCOLOR, (w, 1, fw-w-1, h-2))
        pygame.draw.rect(background.image, game.BGCOLOR, (1,1, w-2, h-2), 1)
        desc = text.Text(name2, "small", (x+5, y+21), color=(game.BGCOLOR), border=False)

        self.popup_sprites.append(background)
        self.popup_sprites.append(city)
        self.popup_sprites.append(desc)

        savestate = self.game.save.get_level_state(self.selected_level)

        for i in range(3):
            star = framesprite.FrameSprite("assets/star.png",13)
            star.move(x + 6 + i * 15, y + 32)
            if i < savestate['stars']:
                star.set_frame(1)
            self.popup_sprites.append(star)

        if savestate['beaten']:
            steptext = "%d Steps" % savestate['steps']
            stepwidth = text.FONTS['small'].get_rect(steptext)[2]
            steps = text.Text(steptext, "small", (x + w - 6 - stepwidth, y + 35), color=(game.BGCOLOR),border=False)
            self.popup_sprites.append(steps)

        self.make_minimap(x + w, y + 7)

        self.back_group.add(self.popup_sprites)

        city_index = CITIES.index(name1)
        if name1 == CITIES[0]:
            self.prev_text.set_pos(0, -20)
        else:
            self.prev_text.set_text("< " + CITIES[city_index - 1])
            self.prev_text.set_pos(5, 160)
        if name1 == CITIES[-1]:
            self.next_text.set_pos(0, -20)
        else:
            self.next_text.set_text(CITIES[city_index + 1] + " >")
            self.next_text.set_pos(235 - self.next_text.rect[2], 160)



    def make_minimap(self, x, y):
        background = pygame.sprite.Sprite()
        
        background.image = pygame.Surface((42,34))
        background.rect = (x, y, 42, 34)
        background.image.fill(game.BGCOLOR)
        self.popup_sprites.append(background)

        ts = tilemap.Tilemap(2, 20, 16, pygame.image.load(resource_path('assets/minitiles.png')))
        ts.load(resource_path('levels/%s_tiles.csv' % LEVELS[self.selected_level][0]))
        ts.rect = (x + 1, y + 1, ts.rect[2], ts.rect[3])
        self.popup_sprites.append(ts)

        ts = tilemap.Tilemap(2, 20, 16, pygame.image.load(resource_path('assets/miniobjects.png')), use_zero=True)
        ts.load(resource_path('levels/%s_objects.csv' % LEVELS[self.selected_level][0]))
        ts.rect = (x + 1, y + 1, ts.rect[2], ts.rect[3])
        self.popup_sprites.append(ts)    

    def take_input(self, inp, event):
        if inp == "right":
            self.selected_level = min(self.selected_level + 1, len(LEVELS)-1)
            self.update_selection()
            sound.play("blip")

        elif inp == "back":
            self.game.go_to_menu()

        elif inp == "left":
            self.selected_level = max(self.selected_level - 1, 0)
            self.update_selection()
            sound.play("blip")

        elif inp == "action":
            sound.play("step2")
            self.game.start_level(LEVELS[self.selected_level][0], self.selected_level)

        elif inp == "click":
            print((event.pos[0] // game.SCALE + self.scroll[0], event.pos[1] // game.SCALE + self.scroll[1]))

        elif inp == "other" and game.DEV:
            if event.key == pygame.K_c:
                self.game.save.level_state = {}
                
            if event.key == pygame.K_b:
                self.game.save.set_level_state(self.selected_level, True, 1, 3)

            if event.key == pygame.K_s:
                self.game.save.save()
                self.game.return_to_map()
                
    def update(self, dt):
        scene.Scene.update(self, dt)
        self.animation_timer += dt
        if self.animation_timer > 0.38:
            self.animation_timer -= 0.38
            for sprite in self.animated:
                sprite.step_animation() 
            self.flash_index = (self.flash_index + 1) % 2
            self.next_text.color = [(247, 249, 223), (67, 201, 40)][self.flash_index]
            self.next_text.update()
            self.prev_text.color = [(247, 249, 223), (67, 201, 40)][self.flash_index]
            self.prev_text.update()