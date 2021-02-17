import json
from resources import resource_path

DEFAULT_SETTINGS = {
    'music_volume': 5,
    'sound_volume': 5,
    'scale': 2,
    'showed_credits': False
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
        self.settings = data.get("settings", DEFAULT_SETTINGS)
        SAVE_OBJ = self

    def save(self):
        data = {
            'level_state': self.level_state,
            'settings': self.settings
        }
        json.dump(data, open(resource_path(FILENAME), "w"))

    def get_level_state(self, level_index):
        if level_index not in self.level_state:
            return {'beaten':False, 'steps':0, 'stars':0}

        else:
            return self.level_state[level_index]

    def set_level_state(self, level_index, beaten, steps, stars):
        self.level_state[level_index] = {'beaten':beaten, 'steps':steps, 'stars':stars}

    def get_setting(self, key):
        return self.settings.get(key, DEFAULT_SETTINGS[key])

    def set_setting(self, key, value):
        self.settings[key] = value
