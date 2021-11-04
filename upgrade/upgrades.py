import csv
from collections import defaultdict

from colors import *
from stats import Stats

write_spreadsheet = False
if write_spreadsheet:
    w = csv.writer(open("spreadsheet.csv", "w"))

UPGRADES = {
    'iron':defaultdict(list),
    'ice':defaultdict(list),
    'gas':defaultdict(list),
}

UPGRADE_CATEGORY_COLORS = {
    'buildings':PICO_LIGHTGRAY,
    'ships':PICO_GREEN,
    'tech':PICO_ORANGE,
}

class Upgrade:
    name = ""
    title = "Not Implemented"
    description = ""
    cursor = None
    icon = None
    stats = Stats()
    requires = ()
    infinite = False
    family = None
    alien = False
    alien_name = None
    alien_min_level = 0 # Minimum level this is researchable
    
    def apply(self, to):
        pass


UPGRADE_CLASSES = {}
ALL_UPGRADE_CLASSES = []

def register_upgrade(cls):
    UPGRADE_CLASSES[cls.name] = cls
    UPGRADES[cls.resource_type][cls.category].append(cls.name)
    ALL_UPGRADE_CLASSES.append(cls)
    if write_spreadsheet:
        print(cls)
        try:
            w.writerow([cls.category, cls.resource_type, cls.family['tree'], cls.title, cls.description])
        except:
            pass
    return cls

from upgrade import building_upgrades, ship_upgrades, tech_upgrades
