import pygame
import save
from resources import resource_path

MUSIC_ENDEVENT = pygame.USEREVENT+1

SOUNDFILES = {
    'step0':'assets/Step0.wav',
    'step1':'assets/Step1.wav',
    'step2':'assets/Step2.wav',
    'occupy':'assets/Occupy2.wav',
    'factory':'assets/Factory.wav',
    'blip':'assets/Blip.wav',
    'soldier':'assets/Soldier.wav',
    'cannot':'assets/Cannot.wav',
    'cell':'assets/Cell.wav',
    'defeat':'assets/Defeat.wav',
    'tankfire':'assets/TankFire.wav',
    'tankdrive':'assets/TankDrive.wav'
}
SOUNDS = {}

def init():
    for s,fn in SOUNDFILES.items():
        SOUNDS[s] = pygame.mixer.Sound(resource_path(fn))
    pygame.mixer.music.set_endevent(MUSIC_ENDEVENT)

def play(name):
    vol = save.SAVE_OBJ.get_setting("sound_volume") / 10
    if vol > 0:
        SOUNDS[name].play().set_volume(vol)


MUSIC = {
    'overworld':resource_path('assets/menusong.ogg'),
    'game':resource_path('assets/menusong.ogg'),
    'victory':resource_path('assets/newvictory.ogg'),
}
MUSIC_TIMES = {
    'overworld':{'last_start':0, 'pause_pos':0},
    'game':{'last_start':0, 'pause_pos':0},
    'victory':{'last_start':0, 'pause_pos':0}
}
LAST_TRACK = None
CURRENT_TRACK = None

def play_music(name, loops=0):
    global CURRENT_TRACK
    CURRENT_TRACK = name
    if name == "victory":
        pygame.mixer.music.load(MUSIC[name])
        pygame.mixer.music.play(loops=0)
        pygame.mixer.music.set_volume(0.2 * save.SAVE_OBJ.get_setting("music_volume") / 10) # change?
        return

    global MUSIC_TIMES, LAST_TRACK
    time_played = pygame.mixer.music.get_pos()
    if LAST_TRACK:
        mtlt = MUSIC_TIMES[LAST_TRACK]
        mtlt['pause_pos'] = mtlt['last_start'] + time_played
    mtct = MUSIC_TIMES[name]
    pygame.mixer.music.load(MUSIC[name])
    pygame.mixer.music.play(loops=0)
    pygame.mixer.music.set_pos(mtct['pause_pos'] / 1000.0)
    mtct['last_start'] = mtct['pause_pos']
    update_volume()
    LAST_TRACK = name
    #print(MUSIC_TIMES)

def update_volume():
    pygame.mixer.music.set_volume(0.1 * save.SAVE_OBJ.get_setting("music_volume") / 10)

def stop_music():
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()


def end_of_music():
    #print("End of music")
    if CURRENT_TRACK != "victory":
        MUSIC_TIMES[CURRENT_TRACK]['last_start'] = 0
        MUSIC_TIMES[CURRENT_TRACK]['pause_pos'] = 0
        play_music(CURRENT_TRACK)   