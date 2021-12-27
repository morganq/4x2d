import random

import pygame

import save
from resources import resource_path

MUSIC_ENDEVENT = pygame.USEREVENT+1

SOUNDFILES = {
    'short1':'assets/sounds/short1.wav',
    'short2':'assets/sounds/short2.wav',
    'short3':'assets/sounds/short3.wav',
    'panel':'assets/sounds/panel.wav',
    'attackpanel':'assets/sounds/attackpanel.wav',
    'click1':'assets/sounds/click1.wav',
    'upgrade':'assets/sounds/upgrade.wav',
    'launch':'assets/sounds/launch.wav',
}
SOUNDS = {}

def load_sound(name, fn):
    SOUNDS[name] = pygame.mixer.Sound(resource_path(fn))


def init():
    pygame.mixer.init()
    for s,fn in SOUNDFILES.items():
        SOUNDS[s] = pygame.mixer.Sound(resource_path(fn))
    for name in [
            'laser1', 'laser2', 'laser3', 'explosion1', 'explosion2', 'control', 'upgrade2', 'hit',
            'talk1', 'talk2', 'talk3', 'short3', 'goodcapture', 'badcapture', 'exp1', 'exp2', 'exp3',
            'exp4', 'radar', 'msg1', 'msg2', 'recall', 'cancel', 
        ]:
        load_sound(name, "assets/sounds/%s.wav" % name)            
    pygame.mixer.music.set_endevent(MUSIC_ENDEVENT)

def play_explosion():
    play(random.choice(['exp1', 'exp2', 'exp3', 'exp4']))

def play(name):
    if name not in SOUNDS:
        load_sound(name, "assets/sounds/%s.wav" % name)
        print("UNREGISTERED SOUND", name)
    vol = save.SAVE_OBJ.get_setting("sound_volume") / 10
    if vol > 0:
        channel = SOUNDS[name].play()
        if channel:
            channel.set_volume(vol)


MUSIC = {
    "game":"assets/sounds/Pulse Emitter - Nebula.mp3"
}
MUSIC_TIMES = {
    "game":0
}
LAST_TRACK = None
CURRENT_TRACK = None

def play_music(name, loops=0):
    pygame.mixer.music.load(MUSIC[name])
    pygame.mixer.music.play(loops=0)
    update_volume()

def update_volume():
    pygame.mixer.music.set_volume(0.1 * save.SAVE_OBJ.get_setting("music_volume") / 10)

def stop_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()


def end_of_music():
    pass
