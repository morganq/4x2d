import pygame
import starmap
import states
import text
from button import Button
from colors import *
from scene import Scene
from simplesprite import SimpleSprite
from spritebase import SpriteBase
from text import Text
from upgrade.upgradeicon import UpgradeIcon
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2


class StoreItemButton(SpriteBase):
    def __init__(self, pos, element, name, description, price, bought=False, can_afford=True, onclick=None):
        super().__init__(pos)
        self.element = element
        self.name = name
        self.description = description
        self.price = price
        self.onclick = onclick
        self.bought = bought
        self.can_afford = can_afford
        self.selectable = True
        element.pos = self.pos + V2(3, 12)
        self._generate_image()

    def _generate_image(self, hover=False):
        self._width, self._height = (150,50)

        bgcolor = PICO_WHITE
        if self.bought:
            bgcolor = PICO_YELLOW
        elif not self.can_afford:
            bgcolor = PICO_DARKGRAY
        elif hover:
            bgcolor = PICO_LIGHTGRAY

        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        self.image.fill(bgcolor)

        ts = text.render_multiline(self.name, "tiny", PICO_BLACK, 100)
        self.image.blit(ts, (3, -1))

        ts = text.render_multiline("%d credits" % self.price, "tiny", PICO_BLACK, 50)
        self.image.blit(ts, (self._width - ts.get_width() - 3, -1))

        ts = text.render_multiline(self.description, "tiny", PICO_BLACK, 100, center=False)
        self.image.blit(ts, (33, 12))      

        pygame.draw.polygon(self.image, (0,0,0,0), [
            (self._width - 5,self._height),
            (self._width,self._height - 5),
            (self._width,self._height),
        ], 0)

        self._recalc_rect()

    def on_mouse_enter(self, pos):
        self._generate_image(True)
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        self._generate_image(False)
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        if self.can_afford and not self.bought:
            self.onclick()
        return super().on_mouse_down(pos)               

class StoreState(states.UIEnabledState):
    is_basic_joystick_panel = True
    def __init__(self, scene):
        super().__init__(scene)
        self.tooltip_timer = 0
        self.last_tooltip = None

    def get_joystick_cursor_controls(self):
        return self.scene.buttons

    def joystick_input(self, input, event):
        if input == "back":
            self.scene.on_exit()
        return super().joystick_input(input, event)

    def update(self, dt):
        if self.scene.game.input_mode == "joystick":
            control = self.joystick_overlay.get_current_control()
            if isinstance(control, StoreItemButton) and isinstance(control.element, UpgradeIcon):
                if not control.element._tooltip_panel or not control.element._tooltip_panel.alive():
                    if self.last_tooltip:
                        self.last_tooltip.on_mouse_exit(V2(0,0))
                    control.element.on_mouse_enter(control.element.pos)
                    self.last_tooltip = control.element
            else:
                if self.last_tooltip:
                    self.last_tooltip.on_mouse_exit(V2(0,0))                

        return super().update(dt)

class StoreScene(Scene):
    def __init__(self, game, store):
        super().__init__(game)
        self.offerings = store['offerings']
        self.bought = set()

    def start(self):
        self.background_group = pygame.sprite.Group()
        self.game_group = pygame.sprite.LayeredDirty()
        self.ui_group = pygame.sprite.LayeredDirty()
        self.build_shop()
        self.sm = states.Machine(StoreState(self))

    def build_shop(self):
        self.buttons = []
        self.ui_group.empty()
        t = Text("Shop (MOCKUP)", "big", V2(300, 10) + self.game.game_offset, PICO_BLACK, multiline_width=300)
        t.offset = (0.5, 0)
        self.ui_group.add(t)

        self.credits_text = Text(
            "Your Credits: %d" % self.game.run_info.credits,
            "big",
            V2(300, 30) + self.game.game_offset,
            PICO_GREEN,
            multiline_width=300
        )
        self.credits_text.offset = (0.5, 0)
        self.ui_group.add(self.credits_text)        

        y = 70
        for row in self.offerings:
            name = {
                'memory':'Memory Crystals',
                'o2':'Oxygen Refill',
                'blueprint':'Blueprints',
                'levelup':'Level Up'
            }[row['offer_type']]
            t = Text(name, "small", V2(300, y - 15) + self.game.game_offset, PICO_BLACK, multiline_width=200)
            t.offset = (0.5, 0)
            self.ui_group.add(t)
            fn = {
                'memory':self.create_memory_row,
                'o2':self.create_o2_row,
                'blueprint':self.create_blueprint_row,
                'levelup':self.create_levelup_row
            }[row['offer_type']]

            fn(row, y)
            y += 90
        
        t = "Exit Shop"
        bx = 360
        if self.game.input_mode == "joystick":
            t = "[*circle*] Exit Shop"
            bx = 330
        self.ui_group.add(Button(V2(bx, 325) + self.game.game_offset, t, "big", self.on_exit))

    def update(self, dt):
        for spr in self.ui_group.sprites():
            spr.update(dt)
        return super().update(dt)

    def render(self):
        self.game.screen.fill(PICO_GREYPURPLE)
        self.background_group.draw(self.game.screen)
        self.game_group.draw(self.game.screen)
        self.ui_group.draw(self.game.screen)        
        return super().render()

    def buy(self, product):
        self.bought.add(product)
        self.start()

    def create_memory_row(self, row, y):
        self.buttons.append([])
        def make_onclick(price, upgrade):
            return lambda : self.buy_memory(price, upgrade)
        for i,upgrade in enumerate(row['upgrades']):
            price = 40
            elem = UpgradeIcon(V2(0,0), upgrade, tooltip=True, tooltip_position="bottom")
            u = UPGRADE_CLASSES[upgrade]

            # Adjust price
            if u.resource_type == "ice":
                price += 10
            if u.resource_type == "gas":
                price += 20
            if "2" in u.name:
                price += 20
            if "3" in u.name:
                price += 40

            if len(u.title) > 22:
                title = u.title[0:19] + "..."
            else:
                title = u.title
            sib = StoreItemButton(
                V2(i * 160 + 65, y) + self.game.game_offset,
                elem,
                title,
                "Unlock this Tech for all future encounters.",
                price,
                bought = upgrade in self.bought or upgrade in self.game.run_info.saved_technologies,
                can_afford = self.game.run_info.credits >= price,
                onclick=make_onclick(price, upgrade)
            )
            self.ui_group.add(sib)
            self.ui_group.add(elem)
            self.buttons[-1].append(sib)

    def buy_memory(self, price, upgrade):
        self.game.run_info.credits -= price
        self.game.run_info.saved_technologies.append(upgrade)
        self.buy(upgrade)

    def create_o2_row(self, row, y):
        price = 60
        elem = SimpleSprite(V2(0,0), "assets/i-o2.png")
        sib = StoreItemButton(
            V2(225, y) + self.game.game_offset,
            elem,
            "Oxygen - 600", "Gain +600 seconds of Oxygen.",
            price,
            bought='o2' in self.bought,
            can_afford=self.game.run_info.credits >= price,
            onclick=lambda: self.buy_o2(price, 600)
        )
        self.ui_group.add(sib)
        self.ui_group.add(elem)
        self.buttons.append([sib])

    def buy_o2(self, price, quantity):
        self.game.run_info.credits -= price
        self.game.run_info.o2 += quantity
        self.buy("o2")

    def create_blueprint_row(self, row, y):
        self.buttons.append([])
        def make_onclick(price, upgrade):
            return lambda : self.buy_blueprint(price, upgrade)
        for i,upgrade in enumerate(row['upgrades']):
            price = 30
            elem = UpgradeIcon(V2(0,0), upgrade, tooltip=True, tooltip_position="bottom")
            u = UPGRADE_CLASSES[upgrade]
            if u.resource_type == "ice":
                price += 10
            if u.resource_type == "gas":
                price += 20
            if "2" in u.name:
                price += 20
            if "3" in u.name:
                price += 40
            if len(u.title) > 22:
                title = u.title[0:19] + "..."
            else:
                title = u.title
            sib = StoreItemButton(
                V2(i * 160 + 65, y) + self.game.game_offset,
                elem,
                title,
                "Unlock this Building for all future encounters.",
                price,
                bought = upgrade in self.bought or upgrade in self.game.run_info.blueprints,
                can_afford = self.game.run_info.credits >= price,
                onclick=make_onclick(price, upgrade)
            )
            self.ui_group.add(sib)
            self.ui_group.add(elem)
            self.buttons[-1].append(sib)

    def buy_blueprint(self, price, upgrade):
        self.game.run_info.credits -= price
        self.game.run_info.blueprints.append(upgrade)
        self.buy(upgrade)

    def create_levelup_row(self, row, y):
        ship = row['ship']
        elem = SimpleSprite(V2(0,0), "assets/i-%s.png" % ship)
        price = 100
        lvl = self.game.run_info.ship_levels[ship] + 1
        if 'levelup' in self.bought:
            lvl -= 1
        sib = StoreItemButton(
            V2(225, y) + self.game.game_offset,
            elem,
            "%s Level %d" % (ship.title(), lvl),
            "Improve health and damage of all %ss" % ship.title(),
            price,
            bought = 'levelup' in self.bought,
            can_afford = self.game.run_info.credits >= price,
            onclick=lambda: self.buy_levelup(price, ship)
        )
        self.ui_group.add(sib)
        self.ui_group.add(elem)
        self.buttons.append([sib])

    def buy_levelup(self, price, ship):
        self.game.run_info.credits -= price
        self.game.run_info.ship_levels[ship] = min(self.game.run_info.ship_levels[ship] + 1, 3)
        self.buy("levelup")
        
    def on_exit(self):
        self.game.scene = starmap.starmapscene.StarMapScene(self.game)
        self.game.scene.start()
