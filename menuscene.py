import scene
import game
import save
import text
import pygame
import simplesprite
import framesprite
import math
import sys
import sound
import creditsscene

class MenuScene(scene.Scene):
    def start(self):
        self.group = pygame.sprite.Group()
        bg = simplesprite.SimpleSprite("assets/menubg.png", (0,0))
        self.group.add(bg)

        self.selected_item_index = 0
        
        self.items = {}

        self.items['start'] = text.Text("START", "small", (20, 75))
        self.items['music'] = text.Text("MUSIC", "small", (20, 90))
        self.items['sound'] = text.Text("SOUND", "small", (20, 105))
        self.items['resolution'] = text.Text("RESOLUTION", "small", (20, 120))
        self.items['credits'] = text.Text("CREDITS", "small", (20, 135))
        self.items['exit'] = text.Text("EXIT", "small", (20, 150))
        
        self.item_names = list(self.items.keys())

        for item in self.items.values():
            self.group.add(item)
        self.update_selection()

        self.music_meter = simplesprite.SimpleSprite("assets/settingmeter.png", (80, 89))
        self.group.add(self.music_meter)
        self.sound_meter = simplesprite.SimpleSprite("assets/settingmeter.png", (80, 104))
        self.group.add(self.sound_meter)
        self.resolution_display = text.Text("1x1", "small", (100, 120))
        self.group.add(self.resolution_display)
        self.update_settings()
        sound.play_music("overworld")

        self.animated = []
        self.add_anim("assets/flag.png", 12, [0,1,2,3], (24,12))
        self.add_anim("assets/worker.png", 12, [2,3], (24,18))
        self.add_anim("assets/factory.png", 12, [0,1,2], (12,18))
        self.add_anim("assets/factory.png", 12, [0,1,2], (12,28))
        self.add_anim("assets/police.png", 12, [4,5], (168,30))
        self.add_anim("assets/police.png", 12, [2,3], (168 + 24,30 +24))
        self.add_anim("assets/soldier.png", 14, [0,1], (144, 150))
        self.add_anim("assets/soldier.png", 14, [0,1], (144, 162))
        self.timer = 0
        
    def add_anim(self, img, width, frames, pos):
        s = framesprite.FrameSprite(img, width)
        self.group.add(s)
        s._image_name = img
        s.allowed_frames = frames
        s.allowed_frame_index = 0
        s.set_frame(frames[0])
        s.move(*pos)
        self.animated.append(s)

    def update(self, dt):
        self.timer += dt
        if self.timer > 0.35:
            self.timer -= 0.35
            for s in self.animated:
                s.allowed_frame_index = (s.allowed_frame_index + 1) % len(s.allowed_frames)
                s.set_frame(s.allowed_frames[s.allowed_frame_index])
                if s._image_name == "assets/flag.png":
                    if s.allowed_frame_index % 2 == 0:
                        s.move(24, 12)
                    else:
                        s.move(24, 11)

    def render(self):
        self.game.screen.fill(game.BGCOLOR)
        self.group.draw(self.game.screen)

    def update_selection(self):
        for key, item in self.items.items():
            if key == self.item_names[self.selected_item_index]:
                item.color = (255, 213, 17)
                item._text = "> " + item._text.split("> ")[-1]
            else:
                item.color = game.FGCOLOR
                item._text = item._text.split("> ")[-1]
            item.update()

    def update_settings(self):
        
        mw = self.game.save.get_setting("music_volume") * 7
        sw = self.game.save.get_setting("sound_volume") * 7
        pygame.draw.rect(self.music_meter.image, (0,0,0,0), (12, 1, 70, 9), 0)
        if mw > 0:
            pygame.draw.rect(self.music_meter.image, (21,97,255,255), (12, 1, mw, 9), 0)
        pygame.draw.rect(self.sound_meter.image, (0,0,0,0), (12, 1, 70, 9), 0)
        if sw > 0:
            pygame.draw.rect(self.sound_meter.image, (21,97,255,255), (12, 1, sw, 9), 0)    

        scale = self.game.save.get_setting("scale")
        self.resolution_display.set_text("%d x %d" % (240 * scale, 192 * scale))

        self.game.save.save()

    def take_input(self, inp, event):
        if inp == "down":
            self.selected_item_index = min(self.selected_item_index + 1, 5)
            self.update_selection()
            sound.play("blip")
        elif inp == "up":
            self.selected_item_index = max(self.selected_item_index - 1, 0)
            self.update_selection()
            sound.play("blip")
        elif inp == "right":
            if self.item_names[self.selected_item_index] == 'music':
                self.game.save.set_setting("music_volume", min(self.game.save.get_setting("music_volume") + 1, 10))
                self.update_settings()
                sound.update_volume()
            if self.item_names[self.selected_item_index] == 'sound':
                self.game.save.set_setting("sound_volume", min(self.game.save.get_setting("sound_volume") + 1, 10))                
                self.update_settings()
                sound.play("step0")
            if self.item_names[self.selected_item_index] == 'resolution':
                self.game.save.set_setting("scale", min(self.game.save.get_setting("scale") + 1, 5))
                self.update_settings()
                self.game.update_scale(self.game.save.get_setting("scale"))
        elif inp == "left":
            if self.item_names[self.selected_item_index] == 'music':
                self.game.save.set_setting("music_volume", max(self.game.save.get_setting("music_volume") - 1, 0))
                self.update_settings()            
                sound.update_volume()
            if self.item_names[self.selected_item_index] == 'sound':
                self.game.save.set_setting("sound_volume", max(self.game.save.get_setting("sound_volume") - 1, 0))
                self.update_settings()
                sound.play("step0")
            if self.item_names[self.selected_item_index] == 'resolution':
                self.game.save.set_setting("scale", max(self.game.save.get_setting("scale") - 1, 1))
                self.update_settings()            
                self.game.update_scale(self.game.save.get_setting("scale"))    
        elif inp == "action":
            if self.item_names[self.selected_item_index] == 'start':
                sound.play("step0")
                self.game.return_to_map()
            if self.item_names[self.selected_item_index] == 'exit':
                sys.exit()
            if self.item_names[self.selected_item_index] == 'credits':
                self.game.scene = creditsscene.CreditsScene(self.game)
                self.game.scene.start()