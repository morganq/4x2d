from scene import Scene
from v2 import V2
import pygame
from colors import *
from background import Background
from .galaxy import Galaxy
import game
import text
import states
from aliens.alien import ALIENS
from .starpath import StarPath
from scrollpanel import ScrollPanel
from .starmapstate import StarMapState
from animrotsprite import AnimRotSprite
from simplesprite import SimpleSprite


# click to pick which galaxy to go to next. galaxy panel shows reward and details. start button.
# animation after selecting

class StarMapScene(Scene):
    def __init__(self, game):
        super().__init__(game)

    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()
        self.sm = states.Machine(StarMapState(self))

        self.background_group.add(Background(V2(0,0), 10))        
        self.scroll_panel = ScrollPanel(V2(-game.RES[0] / 2,-650),(game.RES[0] * 2,1000))

        run_path = self.game.run_info.path
        
        self.galaxies = []
        y = 960
        for r,row in enumerate(self.game.run_info.data):
            self.galaxies.append([])
            for i,column in enumerate(row):
                x = game.RES[0] // 2 - 80 * (len(row) - 1) + 160 * i
                x += game.RES[0] / 2
                alien = ALIENS[column['alien']]
                g = Galaxy(V2(x,y), (r,i), alien, column['rewards'], column['difficulty'], r == len(run_path))
                self.galaxies[-1].append(g)
                for j in column['links']:
                    p2 = g.pos
                    p1 = self.galaxies[-2][j].pos
                    travelled = (
                        len(run_path) > r and
                        run_path[r] == (r, i) and
                        run_path[r-1] == (r-1, j)
                    )
                    path = StarPath(p1,p2,travelled, run_path[-1] == (r-1, j))
                    self.game_group.add(path)
                self.game_group.add(g)

                if len(run_path) <= r:
                    reward_icon = SimpleSprite(V2(x, y), "assets/%s.png" % column['rewards'][0])
                    self.game_group.add(reward_icon)

            y -= 90

        p = self.galaxies[run_path[-1][0]][run_path[-1][1]].pos + V2(3, -14)
        self.colonist = AnimRotSprite(p, 'assets/colonist.png', 12)
        self.colonist.offset = (0.5,0.5)
        self.game_group.add(self.colonist)

    def update(self, dt):
        self.colonist.angle += dt
        for s in self.game_group.sprites():
            s.update(dt)
        super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.scroll_panel.image.fill((0,0,0,0))
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.scroll_panel.image)
        self.ui_group.draw(self.scroll_panel.image)
        self.game.screen.blit(self.scroll_panel.image, self.scroll_panel.pos.tuple_int())
        self.tutorial_group.draw(self.game.screen)
        return super().render()