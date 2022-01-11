from text import Text
from scene import Scene
import pygame
from colors import *
import states
from upgrade import upgrades
import pygame
V2 = pygame.math.Vector2
from upgrade.upgradeicon import UpgradeIcon
import game

class AllUpgradesScene(Scene):
    def __init__(self, game):
        super().__init__(game)

    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.sm = states.Machine(states.UIEnabledState(self))

        ups = {}
        for cat in ['buildings', 'ships', 'tech']:
            ups[cat] = {}
            for res in ['iron', 'ice', 'gas']:
                ups[cat][res] = {}

        for uc in upgrades.UPGRADE_CLASSES.values():
            if uc.alien:
                continue
            f = ups[uc.category][uc.resource_type]
            ft = uc.family['tree']
            if ft in f:
                f[ft].append(uc)
            else:
                f[ft] = [uc]

        for ci,cat in enumerate(ups.keys()):
            category = ups[cat]
            self.game_group.add(Text(cat, "big", V2(ci * 180 + 10, 5), PICO_BLACK))
            y = 25
            for res in category.keys():
                resource = category[res]
                self.game_group.add(Text(res, "small", V2(ci * 180 + 10, y), PICO_BLACK))
                y += 10
                for fam in ups[cat][res]:
                    family = resource[fam]
                    x = 0
                    for up in sorted(family, key=lambda x:int("".join([i for i in x.name if i.isdigit()]))):
                        self.game_group.add(
                            UpgradeIcon(V2(ci * 180 + 10 + x, y), up.name, tooltip=True)
                        )
                        x += 25
                    y += 25
                y += 10


    def render(self):
        self.game.screen.fill(PICO_LIGHTGRAY)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()