import json

from resources import resource_path
from run import RunInfo

DEFAULT_SETTINGS = {
    'music_volume': 5,
    'sound_volume': 5,
    'resolution':None,
    'fullscreen':False,
    'showed_credits': False,
    'controls':{
        1:"confirm",
        2:"back",
        0:"action",
        3:"special",
        4:"game_speed",
        9:"menu",
        8:"cheat1"
    },
}

FILENAME = "save.json"
SAVE_OBJ = None
class Save:
    def __init__(self):
        global SAVE_OBJ
        try:
            data = json.load(open(resource_path(FILENAME), "r"))
        except:
            data = {}

        self.level_state = {int(k):v for k,v in data.get("level_state", {}).items()}
        self.run_state = data.get("run_state", {})
        self.highscores = data.get("highscores", [])
        self.settings = data.get("settings", DEFAULT_SETTINGS)
        self.achievements = data.get("achievements", [])
        self.intel = data.get("intel", [])
        self.victories = data.get("victories", 0)
        self.tutorial_complete = data.get("tutorial_complete", False)
        SAVE_OBJ = self

    def save(self):
        data = {
            'run_state': self.run_state,
            'level_state': self.level_state,
            'highscores': self.highscores,
            'settings': self.settings,
            'achievements': self.achievements,
            'intel': self.intel,
            'victories': self.victories,
            'tutorial_complete': self.tutorial_complete
        }
        json.dump(data, open(resource_path(FILENAME), "w"))

    def get_level_state(self, level_index):
        if level_index not in self.level_state:
            return {'beaten':False, 'steps':0, 'stars':0}

        else:
            return self.level_state[level_index]

    def set_level_state(self, level_index, beaten, steps, stars):
        self.level_state[level_index] = {'beaten':beaten, 'steps':steps, 'stars':stars}

    def set_run_state(self, run):
        if run:
            self.run_state = run.serialize()
        else:
            self.run_state = {}

    def get_run_state(self):
        if self.run_state:
            return RunInfo.deserialize(self.run_state)
        else:
            return RunInfo()

    def get_setting(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS[key])

    def set_setting(self, key, value):
        self.settings[key] = value

    def add_highscore(self, score):
        self.highscores.append(int(score))
        self.highscores.sort(reverse=True)

    def get_highscores(self):
        return self.highscores[0:10]

    def set_achievement(self, name):
        if name not in self.achievements:
            self.achievements.append(name)
            return True
        else:
            return False

    def set_intel(self, name):
        if name not in self.intel:
            self.intel.append(name)
            return True
        else:
            return False
