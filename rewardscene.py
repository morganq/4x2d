import imp
import random

import pygame

import game
import levelstates
import starmap
import states
from button import Button
from colors import *
from intel.inteldata import IntelManager
from rectangle import Rectangle
from scene import Scene
from spritebase import SpriteBase
from text import Text
from upgrade import upgradeicon

V2 = pygame.math.Vector2

REWARDS = {
    'jump_drive':{'title':'Jump Drive', 'description':'Begin with +2 fighters and +1 supply in future battles'},
    'life_support':{'title':'Life Support', 'description': 'Begin with +3 population in future battles'},
    'memory_crystal':{'title':'Memory Crystal', 'description': 'Pick a technology to carry on to future battles'},
    'blueprint':{'title':'Blueprint', 'description': 'Pick a construct to carry on to future battles'},
    'level_fighter':{'title':'Upgrade Fighter', 'description':'Upgrade Fighters to have more health and damage'},
    'level_interceptor':{'title':'Upgrade Interceptors', 'description':'Upgrade Interceptors to have more health and damage'},
    'level_bomber':{'title':'Upgrade Bombers', 'description':'Upgrade Bombers to have more health and damage'},
    'level_battleship':{'title':'Upgrade Battleships', 'description':'Upgrade Battleships to have more health and damage'},
    'o2':{'title':'Oxygen Refill', 'description':'Gain +10 minutes of oxygen'}
}

class RewardSelector(SpriteBase):
    def __init__(self, pos, size, color, border=0):
        super().__init__(pos)
        
        self.image = pygame.Surface(size, pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0,0,size[0] - 1,size[1] - 1), border)
        

class RewardState(states.UIEnabledState):
    is_basic_joystick_panel = True

    def enter(self):
        pos1 = self.scene.game.game_offset + V2(game.RES[0] * 0.1, game.RES[1] / 2 - 75)
        size = (game.RES[0] * 0.8, 150)
        self.scene.ui_group.add(Rectangle(pos1 + V2(-10,-10), (size[0] + 20, size[1] + 20), PICO_BLUE, 1))
        self.scene.ui_group.add(Text("Reward %d of %d" % (self.scene.current_reward_num + 1, self.scene.num_rewards), 'small', pos1, PICO_BLUE, multiline_width=size[0] - 20))
        self.scene.ui_group.add(Text(self.title, 'big', pos1 + V2(0, 20), PICO_YELLOW, multiline_width=size[0] - 20))
        self.scene.ui_group.add(Text(self.description, 'small', pos1 + V2(0, 45), PICO_WHITE, multiline_width=size[0] - 20))

        self.confirm_button = Button(pos1 + V2(size[0], size[1]), "Confirm", "big", self.on_confirm)
        self.confirm_button.offset = (1,1)
        self.scene.ui_group.add(self.confirm_button)
        return super().enter()

    def get_joystick_cursor_controls(self):
        return [[self.confirm_button]]

    def exit(self):
        self.scene.ui_group.empty()
        return super().exit()

    def on_confirm(self):
        self.scene.setup_next_reward()

class CreditsRewardState(RewardState):
    def __init__(self, scene, quantity):
        RewardState.__init__(self, scene)
        self.title = "Bonus Credits"
        self.description = "Gain [^+30] credits for victory, and [^+%d] credits for unused Assets" % (quantity - 30)
        self.quantity = quantity

    def on_confirm(self):
        self.scene.game.run_info.credits += self.quantity
        self.scene.game.run_info.bonus_credits = 0
        IntelManager.inst.give_intel("credits")
        return super().on_confirm()

class OxygenRewardState(RewardState):
    def __init__(self, scene):
        RewardState.__init__(self, scene)
        self.title = REWARDS['o2']['title']
        self.description = REWARDS['o2']['description']

    def on_confirm(self):
        self.scene.game.run_info.o2 += 60 * 10
        self.scene.game.run_info.reward_list.append({"name":"o2"})
        return super().on_confirm()

class JumpDriveRewardState(RewardState):
    def __init__(self, scene):
        RewardState.__init__(self, scene)
        self.title = REWARDS['jump_drive']['title']
        self.description = REWARDS['jump_drive']['description']

    def on_confirm(self):
        self.scene.game.run_info.bonus_fighters += 2
        self.scene.game.run_info.bonus_supply += 1
        self.scene.game.run_info.reward_list.append({"name":"jump_drive"})
        return super().on_confirm()

class LevelUpRewardState(RewardState):
    def __init__(self, scene, ship_type):
        RewardState.__init__(self, scene)
        self.title = REWARDS['level_%s' % ship_type]['title']
        self.description = REWARDS['level_%s' % ship_type]['description']
        self.ship_type = ship_type

    def on_confirm(self):
        self.scene.game.run_info.ship_levels[self.ship_type] = min(self.scene.game.run_info.ship_levels[self.ship_type] + 1, 3)
        self.scene.game.run_info.reward_list.append({"name":"level_%s" % self.ship_type})
        return super().on_confirm()        

class LifeSupportRewardState(RewardState):
    def __init__(self, scene):
        RewardState.__init__(self, scene)
        self.title = REWARDS['life_support']['title']
        self.description = REWARDS['life_support']['description']

    def on_confirm(self):
        self.scene.game.run_info.bonus_population += 3
        self.scene.game.run_info.reward_list.append({"name":"life_support"})
        return super().on_confirm()

class MemoryCrystalRewardState(RewardState):
    def __init__(self, scene, technologies):
        RewardState.__init__(self, scene)
        self.technologies = technologies
        self.selected = None
        self.title = REWARDS['memory_crystal']['title']
        self.description = REWARDS['memory_crystal']['description']
        self.icons = {}

    def get_joystick_cursor_controls(self):
        if self.icons:
            return [
                list(self.icons.values()),
                [self.confirm_button]
            ]
        else:
            return [[self.confirm_button]]

    def enter(self):
        self.selector = RewardSelector(V2(-3,-3), (29,29), PICO_BLUE, 2)
        self.selector.visible = False
        self.scene.ui_group.add(self.selector)

        self.icons = {}

        
        selected_technologies = list(set(self.technologies))
        random.shuffle(selected_technologies)
        selected_technologies = selected_technologies[0:4]
        l = len(selected_technologies)
        for i,technology in enumerate(selected_technologies):
            p = V2(i * 50 - (l - 1) * 50 / 2 - 12 + game.RES[0] / 2, game.RES[1] / 2) + self.scene.game.game_offset
            icon = upgradeicon.UpgradeIcon(p, technology, self.select_technology, True, "bottom")
            self.icons[technology] = icon
            self.scene.ui_group.add(icon)

        RewardState.enter(self)

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
        self.scene.game.run_info.reward_list.append({"name":"memory_crystal"})
        return super().on_confirm()

class BlueprintRewardState(RewardState):
    def __init__(self, scene, buildings):
        RewardState.__init__(self, scene)
        self.buildings = buildings
        self.selected = None
        self.title = REWARDS['blueprint']['title']
        self.description = REWARDS['blueprint']['description']
        self.icons = {}

    def get_joystick_cursor_controls(self):
        if self.icons:
            return [
                list(self.icons.values()),
                [self.confirm_button]
            ]
        else:
            return [[self.confirm_button]]

    def enter(self):
        self.selector = RewardSelector(V2(-3,-3), (29,29), PICO_BLUE, 2)
        self.selector.visible = False
        self.scene.ui_group.add(self.selector)

        self.icons = {}

        selected_buildings = list(set(self.buildings))
        random.shuffle(selected_buildings)
        selected_buildings = selected_buildings[0:4]
        l = len(selected_buildings)
        for i,building in enumerate(selected_buildings):
            p = V2(i * 50 - (l - 1) * 50 / 2 - 12 + game.RES[0] / 2, game.RES[1] / 2) + self.scene.game.game_offset
            icon = upgradeicon.UpgradeIcon(p, building, self.select_building, True, "bottom")
            self.icons[building] = icon
            self.scene.ui_group.add(icon)

        RewardState.enter(self)

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
        self.scene.game.run_info.reward_list.append({"name":"blueprint"})
        return super().on_confirm()        

class RewardScene(Scene):
    def __init__(self, game, technologies, buildings):
        super().__init__(game)
        self.technologies = technologies
        self.buildings = buildings
        self.num_rewards = 0
        self.current_reward_num = 0

    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.tutorial_group = pygame.sprite.Group()
        self.sm = states.Machine(None)

        self.rewards = self.game.run_info.get_path_galaxy()['rewards'][::]
        if self.game.run_info.bonus_credits > 0:
            self.rewards.append("credits")
        self.num_rewards = len(self.rewards)
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
            elif reward == "credits":
                self.sm.transition(CreditsRewardState(self, self.game.run_info.bonus_credits))
            elif reward in ["level_fighter", "level_interceptor", "level_bomber", "level_battleship"]:
                ship_type = reward.split("level_")[1]
                self.sm.transition(LevelUpRewardState(self, ship_type))
            elif reward == "o2":
                self.sm.transition(OxygenRewardState(self))
            else:
                print(reward)
            self.current_reward_num += 1
        else:
            # Give rerolls also
            self.game.run_info.rerolls += 2
            self.game.scene = starmap.starmapscene.StarMapScene(self.game)
            self.game.scene.start()

    def update(self, dt):
        for spr in self.ui_group.sprites():
            spr.update(dt)
        return super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_BLACK)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        self.tutorial_group.draw(self.game.screen)
