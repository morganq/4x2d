import random
from upgrade.upgrades import UPGRADE_CLASSES


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
        self.credits = 20
        self.bonus_credits = 0

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
        obj['credits'] = self.credits
        obj['bonus_credits'] = self.bonus_credits
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
        r.credits = obj['credits']
        r.bonus_credits = obj['bonus_credits']
        return r

    def choose_path(self, row, column):
        self.path.append((row, column))

    def get_path_galaxy(self, index = -1):
        (r,c) = self.path[index]
        return self.data[r][c]

    def new_galaxy(self, row, from_links, level):
        return {
            'node_type':'galaxy',
            'alien': random.choice(['alien1', 'alien2', 'alien3']),
            'rewards': [random.choice(['memory_crystal', 'life_support', 'jump_drive', 'blueprint'])],
            'difficulty': row,
            'level':level,
            'links': from_links
        }        

    def new_store(self, row, from_links):
        offerings = []
        offer_types = ['memory', 'blueprint', 'o2']
        random.shuffle(offer_types)
        for i in range(3):
            offer_type = offer_types.pop()
            offering = {'offer_type':offer_type}
            if offer_type == 'o2':
                offering['quantity'] = 600
            elif offer_type == 'memory':
                techs = [n for n,u in UPGRADE_CLASSES.items() if u.category == "tech" and not u.alien]
                random.shuffle(techs)
                offering['upgrades'] = techs[0:3]
            elif offer_type == 'blueprint':
                techs = [n for n,u in UPGRADE_CLASSES.items() if u.category == "buildings" and not u.alien]
                random.shuffle(techs)
                offering['upgrades'] = techs[0:3]
            offerings.append(offering)

        return {
            'node_type':'store',
            'offerings':offerings,
            'links': from_links
        }


    def generate_run(self):
        self.data = []

        all_levels = ['belt', 'scatter', 'enemysplit', 'choke', 'neighbors', 'tunnel', 'bases', 'cross']
        l1 = all_levels[::]
        random.shuffle(l1)
        l2 = all_levels[::]
        random.shuffle(l2)
        levels = l1 + l2

        for row in range(9):
            level = levels.pop()
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
                if row == 3 or row == 6:
                    node = self.new_store(row, from_links)
                else:
                    node = self.new_galaxy(row, from_links, level)
                self.data[-1].append(node)
        return self.data                 
