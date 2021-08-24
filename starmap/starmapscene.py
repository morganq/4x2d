import game
import pygame
import states
import text
from aliens.alien import ALIENS
from animrotsprite import AnimRotSprite
from background import Background
from colors import *
from scene import Scene
from scrollpanel import ScrollPanel
from simplesprite import SimpleSprite
from store.storenode import StoreNodeGraphic
from v2 import V2

from .galaxy import Galaxy
from .starmapstate import StarMapState
from .starpath import StarPath

# click to pick which galaxy to go to next. galaxy panel shows reward and details. start button.
# animation after selecting

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

        self.background_group.add(Background(V2(0,0), 10, size=(1150,1500)))        
        self.scroll_panel = ScrollPanel(V2(0,0),(1100,1250))

        run_path = self.game.run_info.path
        
        self.galaxies = []
        y = 990
        for r,row in enumerate(self.game.run_info.data):
            self.galaxies.append([])
            for i,column in enumerate(row):
                x = 600 - 80 * (len(row) - 1) + 160 * i
                obj = None
                if column['node_type'] == 'galaxy':
                    alien = ALIENS[column['alien']]
                    obj = Galaxy(V2(x,y), (r,i), alien, column['rewards'], column['difficulty'], column['level'], column['signal'], r == len(run_path))
                    if len(run_path) <= r:
                        if r < len(self.game.run_info.data) - 1:
                            reward_icon = SimpleSprite(V2(x, y), "assets/%s.png" % column['rewards'][0])
                            reward_icon.layer = 1
                            self.game_group.add(reward_icon)        
                        if column['signal']:
                            exc = SimpleSprite(V2(x - 10, y - 10), "assets/exclamation.png")
                            exc.layer = 2
                            self.game_group.add(exc)

                elif column['node_type'] == 'store':
                    obj = StoreNodeGraphic(V2(x,y), column['offerings'], (r,i), r == len(run_path))
                self.galaxies[-1].append(obj)
                for j in column['links']:
                    p2 = obj.pos
                    p1 = self.galaxies[-2][j].pos
                    travelled = (
                        len(run_path) > r and
                        tuple(run_path[r]) == (r, i) and
                        tuple(run_path[r-1]) == (r-1, j)
                    )
                    path = StarPath(p1,p2,travelled, tuple(run_path[-1]) == (r-1, j))
                    self.game_group.add(path)
                if r > 0:
                    self.game_group.add(obj)

            y -= 90

        p = self.galaxies[run_path[-1][0]][run_path[-1][1]].pos + V2(3, -14)
        self.colonist = AnimRotSprite(p, 'assets/colonist.png', 12)
        self.colonist.offset = (0.5,0.5)
        self.game_group.add(self.colonist)

        self.scroll_panel.scroll(-self.colonist.pos + V2(self.game.game_resolution.x / 2, self.game.game_resolution.y - 50))

        self.ui_group2.add(text.Text("Credits: %d" % self.game.run_info.credits, "small", V2(3,3), PICO_GREEN,shadow=PICO_BLACK))

    def update(self, dt):
        self.colonist.angle += dt
        for s in self.game_group.sprites() + self.ui_group.sprites():
            s._scrolled_offset = self.scroll_panel.pos
            s.update(dt)

        for s in self.ui_group2.sprites():
            s.update(dt)            

        super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.scroll_panel.image.fill((0,0,0,0))
        self.background_group.draw(self.scroll_panel.image)
        self.game_group.draw(self.scroll_panel.image)
        self.ui_group.draw(self.scroll_panel.image)
        self.game.screen.blit(self.scroll_panel.image, self.scroll_panel.pos.tuple_int())
        self.ui_group2.draw(self.game.screen)
        self.tutorial_group.draw(self.game.screen)
        return super().render()
