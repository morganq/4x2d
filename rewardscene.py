from text import Text
import pygame
from scene import Scene
import levelstates
from button import Button
from v2 import V2
import game
import states
from colors import *
import starmap
import random
from upgrade import upgradeicon
from spritebase import SpriteBase

REWARDS = {
    'jump_drive':{'title':'Jump Drive', 'description':'Begin with +2 fighter in future battles'},
    'life_support':{'title':'Life Support', 'description': 'Begin with +2 population in future battles'},
    'memory_crystal':{'title':'Memory Crystal', 'description': 'Pick a technology to carry on to future battles'},
    'blueprint':{'title':'Blueprint', 'description': 'Pick a construct to carry on to future battles'},
}

class RewardSelector(SpriteBase):
    def __init__(self, pos, size, color, border=0):
        super().__init__(pos)
        
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0,0,size[0] - 1,size[1] - 1), border)
        

class RewardState(states.UIEnabledState):
    def enter(self):
        self.scene.ui_group.add(Text(self.title, 'huge', V2(game.RES[0] / 2, 60), PICO_BLUE, multiline_width=400, offset=(0.5,0)))
        self.scene.ui_group.add(Text(self.description, 'big', V2(game.RES[0] / 2, 90), PICO_WHITE, multiline_width=300, offset=(0.5,0)))

        confirm_button = Button(V2(game.RES[0]/2, game.RES[1] - 50), "Confirm", "big", self.on_confirm)
        confirm_button.offset = (0.5,0.5)
        self.scene.ui_group.add(confirm_button)
        return super().enter()

    def exit(self):
        self.scene.ui_group.empty()
        return super().exit()

    def on_confirm(self):
        self.scene.setup_next_reward()

class JumpDriveRewardState(RewardState):
    def __init__(self, scene):
        RewardState.__init__(self, scene)
        self.title = REWARDS['jump_drive']['title']
        self.description = REWARDS['jump_drive']['description']

    def on_confirm(self):
        self.scene.game.run_info.bonus_fighters += 2
        return super().on_confirm()

class LifeSupportRewardState(RewardState):
    def __init__(self, scene):
        RewardState.__init__(self, scene)
        self.title = REWARDS['life_support']['title']
        self.description = REWARDS['life_support']['description']

    def on_confirm(self):
        self.scene.game.run_info.bonus_population += 2
        return super().on_confirm()

class MemoryCrystalRewardState(RewardState):
    def __init__(self, scene, technologies):
        RewardState.__init__(self, scene)
        self.technologies = technologies
        self.selected = None
        self.title = REWARDS['memory_crystal']['title']
        self.description = REWARDS['memory_crystal']['description']

    def enter(self):
        RewardState.enter(self)

        self.selector = RewardSelector(V2(-3,-3), (29,29), PICO_BLUE, 2)
        self.selector.visible = False
        self.scene.ui_group.add(self.selector)

        self.icons = {}

        selected_technologies = list(self.technologies)
        random.shuffle(selected_technologies)
        selected_technologies = selected_technologies[0:4]
        l = len(selected_technologies)
        for i,technology in enumerate(selected_technologies):
            p = V2(i * 50 - (l - 1) * 50 / 2 - 12 + game.RES[0] / 2, game.RES[1] / 2 - 11)
            icon = upgradeicon.UpgradeIcon(p, technology, self.select_technology, True)
            self.icons[technology] = icon
            self.scene.ui_group.add(icon)

    def select_technology(self, upgrade, **kwargs):
        self.selector.pos = self.icons[upgrade.name].pos + V2(-1, 0)
        self.selector.visible = True
        self.selected = upgrade

    def on_confirm(self):
        if not self.technologies:
            return super().on_confirm()
        if self.selected == None:
            return
        self.scene.game.run_info.saved_technologies.append(self.selected.name)
        return super().on_confirm()

class BlueprintRewardState(RewardState):
    def __init__(self, scene, buildings):
        RewardState.__init__(self, scene)
        self.buildings = buildings
        self.selected = None
        self.title = REWARDS['blueprint']['title']
        self.description = REWARDS['blueprint']['description']

    def enter(self):
        RewardState.enter(self)

        self.selector = RewardSelector(V2(-3,-3), (29,29), PICO_BLUE, 2)
        self.selector.visible = False
        self.scene.ui_group.add(self.selector)

        self.icons = {}

        selected_buildings = list(self.buildings)
        random.shuffle(selected_buildings)
        selected_buildings = selected_buildings[0:4]
        l = len(selected_buildings)
        for i,building in enumerate(selected_buildings):
            p = V2(i * 50 - (l - 1) * 50 / 2 - 12 + game.RES[0] / 2, game.RES[1] / 2 - 11)
            icon = upgradeicon.UpgradeIcon(p, building, self.select_building, True)
            self.icons[building] = icon
            self.scene.ui_group.add(icon)

    def select_building(self, upgrade, **kwargs):
        self.selector.pos = self.icons[upgrade.name].pos + V2(-1, 0)
        self.selector.visible = True
        self.selected = upgrade

    def on_confirm(self):
        if not self.buildings:
            return super().on_confirm()
        if self.selected == None:
            return
        self.scene.game.run_info.blueprints.append(self.selected.name)
        return super().on_confirm()        

class RewardScene(Scene):
    def __init__(self, game, technologies, buildings):
        super().__init__(game)
        self.technologies = technologies
        self.buildings = buildings

    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()
        self.sm = states.Machine(None)

        self.rewards = self.game.run_info.get_path_galaxy()['rewards']
        self.setup_next_reward()

    def setup_next_reward(self):
        if self.rewards:
            reward = self.rewards.pop(0)
            if reward == "memory_crystal":
                self.sm.transition(MemoryCrystalRewardState(self, self.technologies))
            elif reward == 'blueprint':
                self.sm.transition(BlueprintRewardState(self, self.buildings))
            elif reward == 'life_support':
                self.sm.transition(LifeSupportRewardState(self))
            elif reward == 'jump_drive':
                self.sm.transition(JumpDriveRewardState(self))
            else:
                print(reward)
        else:
            self.game.scene = starmap.starmapscene.StarMapScene(self.game)
            self.game.scene.start()

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)
