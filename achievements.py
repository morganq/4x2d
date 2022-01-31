import pygame

import game
import text
from colors import *
from debug import print
from helper import clamp
from resources import resource_path
from spritebase import SpriteBase

STEAM_ENABLED = False
USE_STEAMWORKS = False
steamworks_sdk = None
def init_steam():
    if not STEAM_ENABLED:
        return
        
    global USE_STEAMWORKS
    global steamworks_sdk
    try:
        import steamworks
        steamworks_sdk = steamworks.STEAMWORKS()
        steamworks_sdk.initialize()
        print("USING STEAM")
        print("Steam ID", steamworks_sdk.Users.GetSteamID())
        print("Logged on:", steamworks_sdk.Users.LoggedOn())
        print("RequestCurrentStats:", steamworks_sdk.UserStats.RequestCurrentStats() == True)
        steamworks_sdk.run_callbacks()
        
        
        USE_STEAMWORKS = True
    except Exception as e:
        print(e)
        print("NOT USING STEAM")

ACHIEVEMENT_INFO = {
    'sector_1_won': {'description':'Beat Sector 1', 'name':'Surprise Attack'},
    'sector_2_won': {'description':'Beat Sector 2', 'name':'Alert!'},
    'sector_3_won': {'description':'Beat Sector 3', 'name':'Reinforcements'},
    'sector_4_won': {'description':'Beat Sector 4', 'name':'All In'},
    'sector_5_won': {'description':'Beat Sector 5', 'name':'Breakthrough'},
    'sector_6_won': {'description':'Beat Sector 6', 'name':'Discovery'},
    'sector_7_won': {'description':'Beat Sector 7', 'name':'Stronghold'},
    'sector_8_won': {'description':'Beat Sector 8', 'name':'Shop'},
    'sector_9_won': {'description':'Beat Sector 9', 'name':'Signal Source'},
    'sector_won_under_3m': {'description':'Beat a Sector in under 3 minutes', 'name':'Quick Work Gold'},
    'sector_won_under_4m': {'description':'Beat a Sector in under 4 minutes', 'name':'Quick Work Silver'},
    'sector_won_under_5m': {'description':'Beat a Sector in under 5 minutes', 'name':'Quick Work Bronze'},
    'sector_won_after_o2_depleted': {'description':'Beat a Sector after oxygen has run out', 'name':'In The Red'},
    'sector_won_zero_lost_ships': {'description':'Beat a Sector without losing a ship', 'name':'No-one Left Behind'},
    'beat_game': {'description':'Defeated the Federation Mothership!', 'name':'First Victory!'},
}

class Achievements:
    inst = None
    def __init__(self, save):
        Achievements.inst = self
        self.save = save

    def grant_achievement(self, name):
        if name not in ACHIEVEMENT_INFO:
            return

        was_new = self.save.set_achievement(name)
        self.save.save()

        if USE_STEAMWORKS:
            print("SET ACHIEVEMENT", name)
            steamworks_sdk.UserStats.SetAchievement(name.encode("ascii"))
            steamworks_sdk.UserStats.StoreStats()
            #steamworks_sdk.run_callbacks()

        else:
            if was_new:
                game.Game.inst.show_achievement(ACHIEVEMENT_INFO[name]['name'], ACHIEVEMENT_INFO[name]['description'])


    def reset_all(self):
        if USE_STEAMWORKS:
            steamworks_sdk.UserStats.ResetAllStats(True)
            steamworks_sdk.UserStats.StoreStats()

    def sector_won(self, sector_number, sector_time_taken, oxygen_left, upgrades_gained, num_ships_lost):
        self.grant_achievement("sector_%d_won" % sector_number)
        if sector_time_taken <= 60 * 3:
            self.grant_achievement("sector_won_under_3m")
        elif sector_time_taken <= 60 * 4:
            self.grant_achievement("sector_won_under_4m")
        elif sector_time_taken <= 60 * 5:
            self.grant_achievement("sector_won_under_5m")

        if oxygen_left < 0:
            self.grant_achievement("sector_won_after_o2_depleted")

        if num_ships_lost == 0:
            self.grant_achievement("sector_won_zero_lost_ships")

    def run_won(self, run_time_taken, oxygen_left, ships_lost, all_rewards, all_upgrades_by_sector):
        self.grant_achievement('beat_game')
        all_upgrades_total = []
        for k,v in all_upgrades_by_sector.items():
            all_upgrades_total.extend(v)
        

    def rewards_claimed(self, all_rewards):
        pass

    def time_passed(self, time_taken, oxygen_left):
        pass

    def ship_gained(self, ship, num_ships):
        pass
        #self.grant_achievement("%s_trained" % ship)


class AchievementPopup(SpriteBase):
    POPUP_TIME = 0.25
    DITHER_TIME = 0.1
    TOTAL_TIME = POPUP_TIME + DITHER_TIME
    KILL_TIME = 6.0

    def __init__(self, pos, name, description):
        super().__init__(pos)
        self.name = name
        self.description = description
        self.time = -self.TOTAL_TIME
        self.offset = (0.5, 0)
        self.dither_image = pygame.image.load(resource_path("assets/dither_white.png")).convert_alpha()
        self._generate_image()

    def _generate_image(self):
        t = clamp((self.time + self.TOTAL_TIME) * (1 / self.TOTAL_TIME), 0, 1)
        t2 = clamp((self.time - (self.KILL_TIME - 0.25)) * 4, 0, 1)
        self._height = t * 50 + 1
        self._width = (1-t2) * 250

        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)


        if self.time < 0:
            self.image.fill(PICO_WHITE)
        else:
            self.image.fill(PICO_BLACK)

            s1 = text.render_multiline(self.name, "small", PICO_YELLOW, 220, True)
            self.image.blit(s1, (self._width // 2 - s1.get_width() // 2, 8))

            s2 = text.render_multiline(self.description, "small", PICO_WHITE, 220, True)
            self.image.blit(s2, (self._width // 2 - s2.get_width() // 2, self._height // 2 + 8 - s2.get_height() // 2))

        if self._height >= 4:
            pygame.draw.rect(self.image, PICO_PINK, (1,1,self._width - 2, self._height - 2), 1)

        if self.time >= 0 and self.time < self.DITHER_TIME:
            self.image.blit(self.dither_image, (0,0))

        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        self._generate_image()
        if self.time > self.KILL_TIME:
            self.kill()
        return super().update(dt)
