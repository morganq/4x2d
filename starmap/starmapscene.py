import button
import game
import pygame
import states
import text
from aliens.alien import ALIENS
from animrotsprite import AnimRotSprite
from background import Background
from colors import *
from constants import REWARD_ICONS_ORDER
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


class NodeSprite(SimpleSprite):
    def __init__(self, run_info, node_pos, pos, img=None):
        super().__init__(pos, img=img)
        self.run_info = run_info
        self.node_pos = node_pos
        self.selectable = self.is_pickable()
        if game.DEV:
            self.selectable = True

    def get_node(self):
        return self.run_info.data[self.node_pos[0]][self.node_pos[1]]

    def is_pickable(self):
        sector, index = self.node_pos
        node = self.run_info.data[sector][index]
        last_beaten_node_pos = self.run_info.path[-1]
        from_node_positions = [(node['sector'] - 1, index) for index in node['links']]
        return (
            last_beaten_node_pos in from_node_positions
        )

    def is_travelled(self):
        return self.node_pos in self.run_info.path

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
        self.time = 0
        self.game.save.set_run_state(self.game.run_info)
        self.game.save.save()
        
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.display_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()
        
        if self.game.run_info.reward_list:
            rewards_width = len(self.game.run_info.reward_list) * 23 + 200
        else:
            rewards_width = 160

        self.background = starmapbackground.StarmapBackground(V2(0,0), rewards_width)
        self.background_group.add(self.background)

        backtext = "BACK"
        if self.game.input_mode == "joystick": backtext = "[*circle*] BACK"
        self.back = button.Button(V2(5, 5), backtext, "big", self.on_back, color=PICO_WHITE)
        self.ui_group.add(self.back)        

        run_path = self.game.run_info.path
        res = self.game.game_resolution
        
        self.grid = []
        self.nodes = []
        x = 30 + self.game.game_offset.x
        base_y = self.background.center_y / 2
        max_per_row = max([len(row) for row in self.game.run_info.data])
        for r,row in enumerate(self.game.run_info.data):
            self.grid.append([])
            for i,column in enumerate(row):
                scaling = 54 - (max_per_row * 8)
                y = base_y - scaling * (len(row) - 1) + (scaling * 2) * i
                obj = None
                reward = None
                if column['node_type'] == 'galaxy':
                    alien = ALIENS[column['alien']]
                    img = "assets/si-alien.png"
                    if column['mods']:
                        img = "assets/si-alien-mod.png"
                    if r == len(self.game.run_info.data) - 1:
                        img = "assets/si-signal.png"
                    obj = NodeSprite(self.game.run_info, (r,i), V2(x,y), img)
                    obj.offset = (0.5,0.5)
                    if column['rewards']:
                        reward = FrameSprite(V2(x + 7,y + 15), "assets/reward_icons.png", 23)
                        reward.frame = REWARD_ICONS_ORDER[column['rewards'][0]]
                        reward.offset = (0.5,0.5)    

                elif column['node_type'] == 'store':
                    obj = NodeSprite(self.game.run_info, (r,i), V2(x,y), "assets/si-shop.png")
                    obj.offset = (0.5,0.5)

                self.grid[-1].append(obj)
                for j in column['links']:
                    p2 = obj.pos
                    p1 = self.grid[-2][j].pos
                    prev_obj = self.grid[-2][j]
                    path = StarPath(p1,p2,obj.is_travelled() and prev_obj.is_travelled(), obj.is_pickable() and prev_obj.is_travelled())
                    self.game_group.add(path)
                if obj.is_travelled():
                    if r < len(run_path) - 1:
                        o = SimpleSprite(obj.pos, "assets/si-traveled.png")
                        o.offset = (0.5,0.5)
                        self.game_group.add(o)
                else:
                    self.nodes.append(obj)
                    self.game_group.add(obj)
                    if reward:
                        self.ui_group.add(reward)

            x += 60

        p = self.grid[run_path[-1][0]][run_path[-1][1]].pos
        self.colonist = SimpleSprite(p, 'assets/si-player.png')
        self.colonist.offset = (0.5,0.5)
        self.game_group.add(self.colonist)
        ry = self.background.center_y
        m,s = divmod(self.game.run_info.o2, 60)
        o2_format = "%d:%02d" % (m,s)
        t1 = text.Text("Credits | [>%d]" % self.game.run_info.credits, "small", V2(res.x / 2 + rewards_width / 2 - 64, ry - 3), PICO_DARKBLUE, multiline_width=150)
        t1.offset = (1, 0)
        self.ui_group.add(t1)

        t2 = text.Text("O2 | [>%s]" % o2_format, "small", V2(res.x / 2 + rewards_width / 2 - 5, ry - 3), PICO_DARKBLUE, multiline_width=150)
        t2.offset = (1, 0)
        self.ui_group.add(t2)    

        if self.game.run_info.reward_list:
            t3 = text.Text("Acquired |", "small", V2(res.x / 2 - rewards_width / 2 + 8, ry - 3), PICO_BLACK)
            self.ui_group.add(t3)
            rx = t3.x + 61
            for r in self.game.run_info.reward_list:
                reward = RewardWithBackground(V2(rx, ry + 1), r['name'])
                reward.offset = (0.5,0.5)  
                self.game_group.add(reward)          
                rx += 23
        else:
            t1.offset = (0.5, 0)
            t1.x = res.x/2 - 30
            t2.offset = (0.5, 0)
            t2.x = res.x/2 + 30
            
        self.sm = states.Machine(StarMapState(self))

    def update(self, dt):
        self.time += dt
        self.colonist.offset = (V2.from_angle(self.time * 3) * 0.05 + V2(0.5,0.5)).tuple()
        for s in self.game_group.sprites() + self.ui_group.sprites():
            s.update(dt)

        super().update(dt)

    def on_back(self):
        self.game.set_scene("menu")

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)
        self.display_group.draw(self.game.screen)
        self.tutorial_group.draw(self.game.screen)
        return super().render()
