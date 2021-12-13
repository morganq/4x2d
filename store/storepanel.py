import game
import pygame
import text
from button import Button
from colors import *
from framesprite import FrameSprite
from panel import Panel
from resources import resource_path
from simplesprite import SimpleSprite
from spritebase import SpriteBase
from starmap import starmapscene
from text import Text
from tooltippanel import TooltipPanel
from upgrade import upgradeicon
from upgrade.upgrades import UPGRADE_CLASSES
from v2 import V2

OFFER_NAMES = {
    'memory_crystal':'Memory Crystals',
    'o2':'Oxygen Refill',
    'blueprint':'Blueprints',
    'levelup':'Ship Upgrades'
}

class ImageButton(FrameSprite):
    def __init__(self, pos, sprite_sheet=None, frame_width=None, onclick=None, tooltip_title=None, tooltip=None):
        super().__init__(pos, sprite_sheet=sprite_sheet, frame_width=frame_width)
        self.selectable = True
        self.onclick = onclick
        self.tooltip = tooltip
        self.tooltip_title = tooltip_title
        self._tooltip_panel = None

    def on_mouse_enter(self, pos):
        if self._tooltip_panel:
            self._tooltip_panel.kill()
        if self.tooltip:
            self._tooltip_panel = TooltipPanel(self.tooltip_title, self.tooltip)
            x = int(-self._tooltip_panel.width / 2 + self.width / 2)
            self._tooltip_panel.pos = self.pos + V2(x,24)
            self._tooltip_panel._reposition_children()
            self.groups()[0].add(self._tooltip_panel)
            self._tooltip_panel.add_all_to_group(self.groups()[0])                 
        return super().on_mouse_enter(pos)

    def on_mouse_exit(self, pos):
        if self.tooltip and self._tooltip_panel:
            self._tooltip_panel.kill()
        return super().on_mouse_exit(pos)

    def on_mouse_down(self, pos):
        self.onclick(self)
        return super().on_mouse_down(pos)

class StorePanelBorder(SpriteBase):
    def __init__(self, offer, pos, width, height):
        super().__init__(pos)
        self.offer = offer
        self.icon_sheet = pygame.image.load(resource_path("assets/reward_icons.png")).convert_alpha()
        self._width = width
        self._height = height
        self._generate_image()

    def _generate_image(self):
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        ts = text.render_multiline(OFFER_NAMES[self.offer], "small", PICO_WHITE, wrap_width=120)
        pygame.draw.rect(self.image, PICO_PINK, (3,4,self._width-6,self._height-7), 1)
        frame = starmapscene.REWARD_ICONS_ORDER[self.offer]
        pygame.draw.rect(self.image, (0,0,0,0), (0,0,ts.get_width() + 15, 13))
        self.image.blit(self.icon_sheet, (-7,-6), (frame * 23,0,23,23))
        self.image.blit(ts, (11,2))

        self._recalc_rect()

class PriceTag(SpriteBase):
    def __init__(self, pos, price_label, bought=False, can_buy=True):
        super().__init__(pos)
        self.price_label = price_label
        self.bought = bought
        self.can_buy = can_buy
        self._generate_image()

    def _generate_image(self):
        ts = text.render_multiline(self.price_label, "small", PICO_BLACK, wrap_width=120)
        w = self._width = ts.get_width() + 7
        h = self._height = 10
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        color = PICO_YELLOW
        if self.bought:
            color = PICO_WHITE
        elif not self.can_buy:
            color = PICO_GREYPURPLE
        pygame.draw.polygon(self.image, color, [
            (0, h // 2),
            (h // 2, 0),
            (w, 0),
            (w, h-1),
            (h//2, h-1)
        ])
        self.image.blit(ts, (5, 1))
        pygame.draw.line(self.image, PICO_BLACK, (h//2, h-1), (w,h-1))
        pygame.draw.line(self.image, PICO_BLACK, (0, h//2),(h//2, h))
        self._recalc_rect()

class StorePanel(Panel):
    def __init__(self, store_data, pos, panel_for, on_done):
        super().__init__(pos, panel_for)
        self.store_data = store_data
        self.on_done = on_done
        self.bought = set()

    def rebuild(self):
        for ci in self._controls:
            ci['control'].kill()
        self._controls = []

        self.add(SimpleSprite(V2(0,0), "assets/shopgraphic.png"), V2(24,0))
        self.add(Text("Shop", "logo", V2(0,0), multiline_width=140), V2(90,12))

        btn = Button(V2(0,0), "Done", "big", self.on_done, color=PICO_WHITE)
        self.add(btn, V2(310,260) - V2(btn.width, btn.height))

        self.add(text.Text("Credits", "small", V2(0,0), PICO_LIGHTGRAY), V2(210, 190))
        self.add(text.Text("%dC" % game.Game.inst.run_info.credits, "big", V2(0,0), PICO_WHITE), V2(210, 205))
        
        self.add_panel(V2(0,0), self.store_data['offerings'][0])
        self.add_panel(V2(1,0), self.store_data['offerings'][1])
        self.add_panel(V2(0,1), self.store_data['offerings'][2])

        self.redraw()
        self.add_all_to_group(self.groups()[0])

    def add_panel(self, gpos, contents):
        panel_pos = V2(gpos.x * 160, gpos.y * 110) + V2(0, 50)
        offer_type = contents['offer_type']
        self.add(StorePanelBorder(offer_type, V2(0,0), 150, 100), panel_pos)

        store_panel_fns = {
            'memory_crystal':lambda pos,contents:self.create_upgrade_panel(pos,contents,self.buy_memory),
            'o2':self.create_o2_panel,
            'blueprint':lambda pos,contents:self.create_upgrade_panel(pos,contents,self.buy_blueprint),
            'levelup':self.create_levelup_panel
        }

        store_panel_fns[offer_type](panel_pos, contents)

    def create_upgrade_panel(self, panel_pos, contents, on_buy):
        positions = [
            V2(20,20),
            V2(85,20),
            V2(20,60),
            V2(85,60)
        ]

        def make_onclick(price, can_buy, upgrade):
            if price and can_buy:
                return lambda x: on_buy(price, upgrade)
            return lambda x: None

        for i,upgrade in enumerate(contents['upgrades']):
            button_pos = positions[i]

            price = 40
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
            
            can_buy = True
            bought = False
            if price > game.Game.inst.run_info.credits:
                can_buy = False            
            if upgrade in self.bought:
                price = None
                can_buy = False
                bought = True

            elem = upgradeicon.UpgradeIcon(V2(0,0), upgrade, tooltip=True, tooltip_position="bottom", onclick=make_onclick(price, can_buy, upgrade))
            self.add(elem, panel_pos + button_pos)
            if can_buy:
                price_title = "%dC" % price
            elif price:
                price_title = "%dC" % price
            else:
                price_title = "SOLD"
            self.add(PriceTag(V2(0,0), price_title, bought=bought, can_buy=can_buy), panel_pos + button_pos + V2(20,2))

    def buy_memory(self, price, upgrade):
        game.Game.inst.run_info.credits -= price
        game.Game.inst.run_info.saved_technologies.append(upgrade)
        self.buy(upgrade)

    def buy_blueprint(self, price, upgrade):
        game.Game.inst.run_info.credits -= price
        game.Game.inst.run_info.blueprints.append(upgrade)
        self.buy(upgrade)        

    def buy(self, product):
        self.bought.add(product)
        self.rebuild()        

    def buy_o2(self, price):
        game.Game.inst.run_info.credits -= price
        game.Game.inst.run_info.o2 += 600
        self.buy("o2")

    def create_o2_panel(self, panel_pos, contents):
        price = 60
        elem = ImageButton(V2(0,0), "assets/i-o2.png", 23, None, tooltip_title="Oxygen Refill", tooltip="[^+10 minutes] of Oxygen")
        def make_onclick(price, can_buy):
            if price and can_buy:
                return lambda x: self.buy_o2(price)
            return lambda x: None        
        button_pos = V2(60, 38)
        can_buy = True
        bought = False
        price_title = "%dC" % price
        if price > game.Game.inst.run_info.credits:
            can_buy = False            
        if 'o2' in self.bought:
            price_title = "SOLD"
            price = None
            can_buy = False
            bought = True        
        elem.onclick = make_onclick(price, can_buy)
        self.add(elem, panel_pos + button_pos)
        self.add(PriceTag(V2(0,0), price_title, bought=bought, can_buy=can_buy), panel_pos + button_pos + V2(20,2))

    def buy_levelup(self, price, ship):
        game.Game.inst.run_info.credits -= price
        game.Game.inst.run_info.ship_levels[ship] = min(game.Game.inst.run_info.ship_levels[ship] + 1, 3)
        self.buy("levelup")

    def create_levelup_panel(self, panel_pos, contents):
        price = 100
        ship = contents['ship']
        level = game.Game.inst.run_info.ship_levels[ship]
        def make_onclick(price, can_buy):
            if price and can_buy:
                return lambda x: self.buy_levelup(price, ship)
            return lambda x: None        
        button_pos = V2(60, 38)
        can_buy = True
        bought = False
        price_title = "%dC" % price
        if price > game.Game.inst.run_info.credits:
            can_buy = False            
        if 'levelup' in self.bought:
            price_title = "SOLD"
            price = None
            can_buy = False
            bought = True        
        if level > 2:
            can_buy = False
            price_title = "SOLD"
        if bought: # If we just bought it, we don't want it to appear to change now that we're higher level
            level -= 1

        elem = ImageButton(
            V2(0,0), "assets/levelups.png", 23, None,
            tooltip_title = "%s Level %d" % (ship.title(), level + 1),
            tooltip="Increase health and damage of all [%ss]" % ship.title()
        )
        elem.frame = {
            ('fighter',1):0,
            ('fighter',2):1,
            ('scout',1):2,
            ('scout',2):3,
            ('interceptor',1):4,
            ('interceptor',2):5,
            ('bomber',1):6,
            ('bomber',2):7,
            ('battleship',1):8,
            ('battleship',2):9,
        }[(ship, level)]

        elem.onclick = make_onclick(price, can_buy)
        self.add(elem, panel_pos + button_pos)
        self.add(PriceTag(V2(0,0), price_title, bought=bought, can_buy=can_buy), panel_pos + button_pos + V2(20,2))  

    def redraw(self):
        xmin, xmax, ymin, ymax = 0,0,0,0
        outerpad = 3
        for ci in self._controls:
            control = ci['control']
            pos = ci['pos']
            xmax = max(pos.x + control.width, xmax)
            ymax = max(pos.y + control.height, ymax)

        box_width = xmax + self.padding * 2
        box_height = ymax + self.padding * 2

        tab_height = 44
        tab_top_width = 115

        self.image = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, PICO_PURPLE, (outerpad, outerpad + tab_height, box_width - outerpad * 2, box_height - outerpad * 2 - tab_height), 0)
        pygame.draw.polygon(self.image, PICO_PURPLE,[
            (outerpad, outerpad + tab_height),
            (outerpad + tab_height, outerpad),
            (outerpad + tab_height + tab_top_width, outerpad),
            (outerpad + tab_height * 2 + tab_top_width, outerpad + tab_height)
        ])
        self._width = box_width
        self._height = box_height

        self._background_offset = V2(self.padding, self.padding)

        self._reposition_children()
        self._recalc_rect()                
