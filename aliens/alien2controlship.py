import sound
from colors import PICO_LIGHTGRAY, PICO_PINK, PICO_YELLOW
from line import Line
from ships.all_ships import register_ship
from ships.fighter import Fighter
from ships.ship import Ship
from v2 import V2


@register_ship
class Alien2ControlShip(Fighter):
    SHIP_NAME = "alien2controlship"
    BASE_HEALTH = 55
    BASE_DAMAGE = 5
    MAX_SPEED = 5
    FIRE_RANGE = 45
    FIRE_RATE = 0.25
    def __init__(self, scene, pos, owning_civ):
        Fighter.__init__(self, scene, pos, owning_civ)
        self.set_sprite_sheet("assets/alien2controlship.png", 13)
        self.tethered = None
        self.tether_end_pos = None
        self.tether_line = None
        self.tether_time = 0

    def get_max_tether_time(self):
        return max(8 * (1 + self.get_stat("alien_control_mul")),2)
        
    def fire(self, at):
        if not isinstance(at, Ship):
            return super().fire(at)

        if self.tethered:
            return

        if at.tether_target:
            return

        sound.play("control")

        at.tether_target = True
        self.tethered = at
        self.tether_end_pos = self.pos + V2(1,0)
        self.tether_line = Line(self.pos, self.tether_end_pos, PICO_PINK)
        self.scene.game_group.add(self.tether_line)

    def update(self, dt):
        if self.tethered:
            delta = self.tethered.pos - self.tether_end_pos
            if delta.sqr_magnitude() > 2 ** 2:
                self.tether_end_pos += delta.normalized() * dt * 15
            else:
                self.tether_end_pos = self.tethered.pos
                self.tether_time += dt
                if self.tether_time > self.get_max_tether_time() / 2:
                    self.tether_line.color = PICO_YELLOW
            self.tether_line.pt1 = self.pos
            self.tether_line.pt2 = self.tether_end_pos
            self.tether_line._generate_image()
            self.tether_line.pos = self.pos

            if self.tether_time > self.get_max_tether_time():
                self.tethered.change_owner(self.owning_civ, self.chosen_target)

            if self.tethered.owning_civ == self.owning_civ:
                self.tethered.tether_target = False
                self.tether_line.kill()
                self.tether_time = 0
                self.tethered = None

            if self.tethered and not self.tethered.is_alive():
                self.tether_line.kill()
                self.tether_time = 0
                self.tethered = None

        return super().update(dt)

    def kill(self):
        if self.tether_line:
            self.tether_line.kill()
        if self.tethered:
            self.tethered.tether_target = False
        return super().kill()
