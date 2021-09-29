import game
import pygame
import states
import text
from aliens.alien import ALIENS
from animrotsprite import AnimRotSprite
from background import Background
from colors import *
from framesprite import FrameSprite
from resources import resource_path
from scene import Scene
from scrollpanel import ScrollPanel
from simplesprite import SimpleSprite
from spritebase import SpriteBase
from store.storenode import StoreNodeGraphic
from v2 import V2

from starmap import starmapbackground

from .galaxy import Galaxy
from .starmapstate import StarMapState
from .starpath import StarPath

# click to pick which galaxy to go to next. galaxy panel shows reward and details. start button.
# animation after selecting

REWARD_ICONS_ORDER = {
    'life_support':0,
    'jump_drive':1,
    'memory_crystal':2,
    'blueprint':3,
    'level_fighter':4,
    'level_interceptor':5,
    'level_bomber':6,
    'level_battleship':7,
}

class RewardWithBackground(SpriteBase):
    def __init__(self, pos, reward_name):
        super().__init__(pos)
        self.reward_name = reward_name
        self.icon_sheet = pygame.image.load(resource_path("assets/reward_icons.png")).convert_alpha()
        self._generate_image()

    def _generate_image(self):
        self._width, self._height = (23,23)
        self.image = pygame.Surface((23,23), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PICO_DARKBLUE, (3, 5, 18, 13), 0)
        pygame.draw.rect(self.image, PICO_DARKBLUE, (2, 6, 20, 11), 0)
        frame_x = REWARD_ICONS_ORDER[self.reward_name] * 23
        self.image.blit(self.icon_sheet, (0,0), (frame_x, 0, 23, 23))




class StarMapScene(Scene):
    def __init__(self, game):
        super().__init__(game)

    def start(self):
        self.game.save.set_run_state(self.game.run_info)
        self.game.save.save()
        
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.ui_group2 = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()
        self.sm = states.Machine(StarMapState(self))

        rewards_width = len(self.game.run_info.reward_list) * 23 + 140

        self.background_group.add(starmapbackground.StarmapBackground(V2(0,0), rewards_width))

        run_path = self.game.run_info.path
        res = self.game.game_resolution
        
        self.grid = []
        x = 30
        max_per_row = max([len(row) for row in self.game.run_info.data])
        for r,row in enumerate(self.game.run_info.data):
            self.grid.append([])
            for i,column in enumerate(row):
                scaling = 54 - (max_per_row * 8)
                y = 110 - scaling * (len(row) - 1) + (scaling * 2) * i
                obj = None
                reward = None
                if column['node_type'] == 'galaxy':
                    alien = ALIENS[column['alien']]
                    #obj = Galaxy(V2(x,y), (r,i), alien, column['rewards'], column['difficulty'], column['level'], column, column['signal'], r == len(run_path))
                    img = "assets/si-alien.png"
                    if column['mods']:
                        img = "assets/si-alien-mod.png"
                    if r == len(self.game.run_info.data) - 1:
                        img = "assets/si-signal.png"
                    obj = SimpleSprite(V2(x,y), img)
                    obj.offset = (0.5,0.5)
                    if column['rewards']:
                        reward = FrameSprite(V2(x + 7,y + 15), "assets/reward_icons.png", 23)
                        reward.frame = REWARD_ICONS_ORDER[column['rewards'][0]]
                        reward.offset = (0.5,0.5)    

                elif column['node_type'] == 'store':
                    obj = SimpleSprite(V2(x,y), "assets/si-shop.png")
                    obj.offset = (0.5,0.5)
                    #obj = StoreNodeGraphic(V2(x,y), column['offerings'], (r,i), r == len(run_path))

                self.grid[-1].append(obj)
                for j in column['links']:
                    p2 = obj.pos
                    p1 = self.grid[-2][j].pos
                    travelled = (
                        len(run_path) > r and
                        tuple(run_path[r]) == (r, i) and
                        tuple(run_path[r-1]) == (r-1, j)
                    )
                    path = StarPath(p1,p2,travelled, tuple(run_path[-1]) == (r-1, j))
                    self.game_group.add(path)
                if r > 0:
                    self.game_group.add(obj)
                    if reward:
                        self.game_group.add(reward)

            x += 60

        p = self.grid[run_path[-1][0]][run_path[-1][1]].pos
        self.colonist = AnimRotSprite(p, 'assets/colonist.png', 12)
        self.colonist.offset = (0.5,0.5)
        self.game_group.add(self.colonist)
        t1 = text.Text("Credits: %d" % self.game.run_info.credits, "small", V2(res.x / 2 + rewards_width / 2 - 8, 217), PICO_BLACK)
        t1.offset = (1, 0)
        self.ui_group.add(t1)
        if self.game.run_info.reward_list:
            t2 = text.Text("Acquired:", "small", V2(res.x / 2 - rewards_width / 2 + 8, 217), PICO_BLACK)
            self.ui_group.add(t2)
            rx = t2.x + 60
            for r in self.game.run_info.reward_list:
                reward = RewardWithBackground(V2(rx, 221), r)
                reward.offset = (0.5,0.5)  
                self.game_group.add(reward)          
                rx += 23
        else:
            t1.offset = (0.5, 0)
            t1.x = res.x/2

    def update(self, dt):
        self.colonist.angle += dt
        for s in self.game_group.sprites() + self.ui_group.sprites():
            s.update(dt)

        super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        self.ui_group2.draw(self.game.screen)
        self.tutorial_group.draw(self.game.screen)
        return super().render()
