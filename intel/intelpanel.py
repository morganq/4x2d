import button
import game
import panel
import pygame
import text
from colors import *
from elements import scrollframe
from spritebase import SpriteBase

from intel.inteldata import *


class IntelBox(SpriteBase):
    def __init__(self, pos, intel_id):
        super().__init__(pos)
        self.intel = INTEL_LOOKUP[intel_id]
        self.enabled = IntelManager.inst.has_intel(intel_id)
        self._generate_image()

    def _generate_image(self):
        w = 400
        nw = 100
        pad = 4
        description = self.intel['description']
        title = self.intel['name']
        color = PICO_WHITE
        if not self.enabled:
            title = "?"
            description = "Gather this intel by exploring more of the game"
            color = PICO_DARKGRAY
        description_surf = text.render_multiline(description, "small", color, wrap_width=w - nw - pad * 2, center=False)
        title_surf = text.render_multiline(title, 'small', color, wrap_width=nw - pad * 2, center=False)
        h1 = description_surf.get_height()
        h2 = title_surf.get_height()
        h = max(h1, h2) + pad * 2
        self.image = pygame.Surface((w,h), pygame.SRCALPHA)
        self.image.fill(PICO_BLACK)
        pygame.draw.rect(self.image, PICO_DARKGRAY, (nw, 0, 1, h), 0)
        self.image.blit(title_surf, (nw // 2 - title_surf.get_width() // 2, h // 2 - h2 // 2))
        self.image.blit(description_surf, (pad * 2 + nw, h // 2 - h1 // 2))
        self._width, self._height = w,h
        self._recalc_rect()

class IntelPanel(panel.Panel):
    def __init__(self, pos, panel_for, on_back):
        super().__init__(pos, panel_for)
        self.on_back = on_back
        self.rebuild_panel()

    def position_nicely(self, scene):
        x,y = scene.game.game_resolution / 2
        self.pos = pygame.Vector2(x - self.width / 2, y - self.height / 2)
        self._reposition_children()

    def rebuild_panel(self):
        self.empty()
        y = 0 
        boxes = []
        for intel in INTEL_ORDER:
            box = IntelBox(pygame.Vector2(0,0), intel['id'])
            boxes.append(box)
            y += box.height + 5
        
        s = pygame.Surface((boxes[0].width, y), pygame.SRCALPHA)
        s.fill(PICO_DARKBLUE)
        y = 0
        for box in boxes:
            s.blit(box.image, (0, y))
            y += box.height + 5
        sf = scrollframe.VScrollFrame(pygame.Vector2(0,0), s, 300)
        self.add(sf, pygame.Vector2(0,0))
        self.scroll_frame = sf

        back = button.Button(pygame.Vector2(0,0), "Back", "small", self.on_back)
        self.add(back, pygame.Vector2(400 - back.width, 350))

        self.redraw()
