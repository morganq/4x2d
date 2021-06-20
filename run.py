import random


class RunInfo:
    def __init__(self, data = None):
        self.data = data or self.generate_run()
        self.path = [(0,0)]
        self.saved_technologies = []
        self.blueprints = []
        self.bonus_population = 0
        self.bonus_fighters = 0
        self.rerolls = 3
        self.o2 = 3600

    def serialize(self):
        obj = {}
        obj['data'] = self.data
        obj['path'] = self.path
        obj['saved_technologies'] = self.saved_technologies
        obj['blueprints'] = self.blueprints
        obj['bonus_population'] = self.bonus_population
        obj['bonus_fighters'] = self.bonus_fighters
        obj['rerolls'] = self.rerolls
        obj['o2'] = self.o2
        return obj
    
    @classmethod
    def deserialize(cls, obj):
        r = RunInfo(obj['data'])
        r.path = obj['path']
        r.saved_technologies = obj['saved_technologies']
        r.blueprints = obj['blueprints']
        r.bonus_population = obj['bonus_population']
        r.bonus_fighters = obj['bonus_fighters']
        r.rerolls = obj['rerolls']
        r.o2 = obj['o2']
        return r

    def choose_path(self, row, column):
        self.path.append((row, column))

    def get_path_galaxy(self, index = -1):
        (r,c) = self.path[index]
        return self.data[r][c]

    def generate_run(self):
        self.data = []
        for row in range(9):
            self.data.append([])
            num_columns = 5 - abs(4 - row)
            for column in range(num_columns):
                if row == 0:
                    from_links = []
                elif row < 5:   
                    from_links = []
                    if column > 0: from_links.append(column - 1)
                    if column < num_columns - 1: from_links.append(column)
                else:
                    from_links = [column, column + 1]
                galaxy = {
                    #'alien': random.choice(['alien1', 'alien2']),
                    'alien': random.choice(['alien3']),
                    'rewards': [random.choice(['memory_crystal', 'life_support', 'jump_drive', 'blueprint'])],
                    'difficulty': row,
                    'level':random.choice(['belt', 'scatter', 'enemysplit', 'choke', 'neighbors', 'tunnel', 'bases', 'cross']),
                    'links': from_links
                } 
                self.data[-1].append(galaxy)
        return self.data                 
