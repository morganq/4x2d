import game
import pygame
import text
from colors import *
from helper import *
from resources import resource_path
from spritebase import SpriteBase

INTEL_ORDER = [
    {'id':'pop', 'name':'Population', 'icon':None, 'description':'Every planet has a maximum population, based on its size. When you have at least one worker on a planet, the worker population gradually multiplies until reaching the maximum. Each worker populating a planet contributes to the planet\'s resource mining.'},
    {'id':'upgrades', 'name':'Upgrades', 'icon':None, 'description':'As you mine resources from planets or asteroids, the bar for that resource in the top-left of the screen increases. When it hits the limit, you are awarded an upgrade of that type - Iron, Ice, or Gas. Each upgrade costs a bit more than the last.'},    
    {'id':'iron', 'name':'Iron', 'icon':None, 'description':'Iron is the least valuable and most common resource. Iron upgrades allow you to construct Fighters and Scouts, build economic and productive buildings, and research basic technologies.'},
    {'id':'ice', 'name':'Ice', 'icon':None, 'description':'Ice is a less common resource. Ice upgrades allow you to construct Interceptors and Bombers, build more sophisticated buildings, and research powerful technologies.'},
    {'id':'gas', 'name':'Gas', 'icon':None, 'description':'Gas is the rarest and most valuable resource. Gas upgrades allow you to construct Battleships, build the most advanced buildings, and research unique technologies.'},
    {'id':'workership', 'name':'Worker Ship', 'icon':None, 'description':'The Worker Ship is used when you want to send Workers from one planet to another. It can hold any number of workers. To take over a planet, you have to send a worker ship to a neutral planet. Destroy an enemy planet to neutralize it, then you can capture it.'},
    {'id':'fighter', 'name':'Fighter', 'icon':None, 'description':'The Fighter is a weak but versitile ship which attacks ships, planets, and asteroids. It has a limited range, and will turn around if it runs out of fuel mid-flight.'},
    {'id':'scout', 'name':'Scout', 'icon':None, 'description':'The Scout is a special-purpose ship for surveilling the enemy and disrupting their economy. Scouts reveal the ships and worker count of enemy planets when they fly near them. They also are equipped with Disruptor Bombs which destroy workers on a target planet. Though weaker than fighters, they are equipped to attack all targets.'},
    {'id':'interceptor', 'name':'Interceptor', 'icon':None, 'description':'The Interceptor is a powerful dogfighting ship. It quickly destroys enemy ships, but is unable to attack planets or asteroids. Requires Ice or Gas to acquire.'},
    {'id':'bomber', 'name':'Bomber', 'icon':None, 'description':'The Bomber is designed to lay waste to planets. However, it has no weapons to defend itself from other ships. Requires Ice or Gas to acquire.'},
    {'id':'battleship', 'name':'Battleship', 'icon':None, 'description':'The Battleship is a powerful, all-purpose capital ship. Requires Gas to acquire.'},
    {'id':'credits', 'name':'Credits', 'icon':None, 'description':'You gain credits at the end of each Sector if you have outstanding upgrades that you have not redeemed. Every game has two shops you can visit to spend these credits on Oxygen, Ship upgrades, Memory Crystals, and Blueprints.'},
    {'id':'o2', 'name':'Oxygen', 'icon':None, 'description':'You begin the game with 60 minutes worth of oxygen. Oxygen is displayed in the top-right corner when playing. If you drop below zero, all your planets and ships will lose health gradually. You can buy more in the Shop if you are running low. '},    
    {'id':'supply', 'name':'Supply', 'icon':None, 'description':'Each ship you\'ve trained takes up 1 supply. Supply is shown in the top right corner. Ship training will pause if you hit the maximum. Every upgrade other than Ship Orders increases your Supply by 1.'},
    {'id':'timeloop', 'name':'Time Loop', 'icon':None, 'description':'Some planets have been locked in a time loop! Capture this planet if you can, as time looped planets will periodically build a copy of the last ship built there.'},
    {'id':'censors', 'name':'Censors', 'icon':None, 'description':'The Censors are the final obstacle. They rule the galaxy, and have coerced all the other civilizations to help them, except us. They must be taken down!'},
    {'id':'timecrystal', 'name':'Time Crystal', 'icon':None, 'description':'The Censors have trapped our allies in time. Destroy the crystals to free them. Every 90 seconds, the crystal freezes time in a large radius. Avoid getting your own ships trapped as well!'},
    {'id':'mothership', 'name':'Mothership', 'icon':None, 'description':'Destroying the Censors\' Mothership is the ultimate goal. The Mothership reclaims several planets when it warps into battle. Enemy ships destroyed near the Mothership will be revived after a brief period. Good luck.'},
]

INTEL_LOOKUP = {row['id']: row for row in INTEL_ORDER}

class IntelManager:
    inst = None
    def __init__(self, save):
        IntelManager.inst = self
        self.save = save

    def give_intel(self, intel_id):
        if intel_id not in INTEL_LOOKUP:
            return

        was_new = self.save.set_intel(intel_id)
        
        if was_new:
            self.save.save()
            game.Game.inst.show_intel(INTEL_LOOKUP[intel_id]['name'])

    def has_intel(self, intel_id):
        return intel_id in self.save.intel

class IntelPopup(SpriteBase):
    POPUP_TIME = 0.25
    DITHER_TIME = 0.1
    TOTAL_TIME = POPUP_TIME + DITHER_TIME
    KILL_TIME = 6.0

    def __init__(self, pos, name):
        super().__init__(pos)
        self.name = name
        self.time = -self.TOTAL_TIME
        self.offset = (0.5, 0)
        self.dither_image = pygame.image.load(resource_path("assets/dither_white.png")).convert_alpha()
        self._generate_image()

    def _generate_image(self):
        t = clamp((self.time + self.TOTAL_TIME) * (1 / self.TOTAL_TIME), 0, 1)
        t2 = clamp((self.time - (self.KILL_TIME - 0.25)) * 4, 0, 1)
        self._height = t * 28 + 1
        self._width = (1-t2) * 250

        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)

        if self.time < 0:
            self.image.fill(PICO_WHITE)
        else:
            self.image.fill(PICO_BLACK)

            s1 = text.render_multiline("New Intel: '%s'" % self.name, "small", PICO_YELLOW, 220, True)
            self.image.blit(s1, (self._width // 2 - s1.get_width() // 2, 6))

            s2 = text.render_multiline("See Intel menu to read it!", "small", PICO_WHITE, 220, True)
            self.image.blit(s2, (self._width // 2 - s2.get_width() // 2, 16))

        if self._height >= 4:
            pygame.draw.rect(self.image, PICO_GREEN, (1,1,self._width - 2, self._height - 2), 1)

        if self.time >= 0 and self.time < self.DITHER_TIME:
            self.image.blit(self.dither_image, (0,0))

        self._recalc_rect()

    def update(self, dt):
        self.time += dt
        self._generate_image()
        if self.time > self.KILL_TIME:
            self.kill()
        return super().update(dt)

