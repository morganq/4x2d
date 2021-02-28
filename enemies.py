import text
import random
from warpwarning import WarpWarning
from ships.alienbattleship import AlienBattleship
from colors import *
from v2 import V2

# - Enemy waves come from outside
#   - Pick targets within some distance from existing enemy planets
#   - 

ADD_FIGHTER_TIME = 17
INVADE_TIME = 26
BATTLESHIP_TIME = 115
BUILDING_TIME = 22

class EnemyController:
    def __init__(self, scene, civ):
        self.scene = scene
        self.civ = civ
        self._status = []
        self.homeworld = None
        
        self.add_fighter_timer = 0
        self.invade_timer = INVADE_TIME - 8
        self.battleship_timer = -60
        self.battleship_wave = 0
        self.building_time = 0

    def update(self, dt):
        self._status = []
        my_planets = self.scene.get_civ_planets(self.civ)
        general_rate = min(0.75 + (len(my_planets) / 6), 2)

        if my_planets:
            if not self.homeworld:
                self.homeworld = my_planets[0]
            self.homeworld.health = self.homeworld.get_max_health()
            self._status.append("planets: " + ", ".join([str(p.pos) for p in my_planets]))            
            self.building_time += dt * general_rate
            if self.building_time > BUILDING_TIME:
                self.building_time = 0
                if random.random() > 0.25:
                    p = random.choice(my_planets)
                    if len(p.buildings) < 5:
                        p.add_building(random.choice(["mining_rate", "regen", "armory"]))
                else:
                    self.civ.upgrade_stats['fire_rate'] += 0.1

            self._status.append(str(dict(self.civ.upgrade_stats)))

            self._status.append("%.2f" % self.add_fighter_timer)
            self.add_fighter_timer += dt * general_rate
            if self.add_fighter_timer > ADD_FIGHTER_TIME:
                p = random.choice(my_planets)
                p.add_ship('alien-fighter')
                self.add_fighter_timer = 0

            self._status.append("%.2f" % self.invade_timer)
            self.invade_timer += dt * general_rate
            near_planets = self.scene.get_planets()
            near_planets.sort(key=lambda x:(x.pos - self.homeworld.pos).sqr_magnitude())
            near_unclaimed = [p for p in near_planets if p.owning_civ != self.civ][0:3]
            self._status.append("near unclaimed: " + ", ".join([str(p.pos) for p in near_unclaimed]))
            if self.invade_timer > max(INVADE_TIME - self.battleship_wave, 4):
                target = random.choice(near_unclaimed)
                my_planets_with_fighters = [p for p in my_planets if p.ships['alien-fighter'] > 0]
                if my_planets_with_fighters:
                    p = random.choice(my_planets_with_fighters)
                    for _ in range(random.randint(1,p.ships['alien-fighter'])):
                        p.emit_ship('alien-fighter', {'to':target})
                    if p.ships['alien-battleship']:
                        for _ in range(random.randint(1,p.ships['alien-battleship'])):
                            p.emit_ship('alien-battleship', {'to':target})
                    if p.population > 1:
                        pop = random.randint(1, p.population-1)
                        p.emit_ship('alien-colonist', {'to':target, 'num':pop})
                    self.invade_timer = 0
                    p.needs_panel_update = True

        self.battleship_timer += dt * general_rate
        if self.battleship_timer > max(BATTLESHIP_TIME / (1 + self.battleship_wave / 4), 20):
            self.battleship_timer = 0
            self.battleship_wave += 1
            near_planets = [
                p for p in self.scene.get_planets()
                if (p.pos - self.homeworld.pos).sqr_magnitude() < (self.battleship_wave * 100) ** 2
            ]
            planet = random.choice(near_planets)
            bsp = planet.pos + V2.from_angle(random.random() * 6.2818) * 40
            ww = WarpWarning(planet, self.scene, bsp)
            self.scene.game_group.add(ww)

    def render(self, screen):
        for i,status in enumerate(self._status):
            text.FONTS['tiny'].render_to(screen, (300, i * 9 + 5), status, PICO_PINK)
            