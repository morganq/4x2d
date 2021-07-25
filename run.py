import random
from math import radians

from upgrade.upgrades import UPGRADE_CLASSES

RUN_INFO_SERIALIZE_FIELDS = [
    'data', 'path', 'saved_technologies', 'blueprints',
    'bonus_population', 'bonus_fighters', 'rerolls', 'o2', 'credits',
    'bonus_credits', 'ship_levels', 'score'
]

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
        self.ship_levels = {'fighter':1, 'interceptor':1, 'bomber':1, 'battleship': 1}
        self.score = 0

        self.next_path_segment = (0,0)

    def serialize(self):
        obj = {}
        for key in RUN_INFO_SERIALIZE_FIELDS:
            obj[key] = getattr(self, key)
        return obj
    
    @classmethod
    def deserialize(cls, obj):
        r = RunInfo("placeholder")
        for key in RUN_INFO_SERIALIZE_FIELDS:
            setattr(r, key, obj[key])
        return r

    def choose_path(self, row, column):
        self.path.append((row, column))

    def get_path_galaxy(self, index = -1):
        (r,c) = self.path[index]
        return self.data[r][c]

    def get_current_level_galaxy(self):
        (r,c) = self.next_path_segment
        return self.data[r][c]        

    def generate_reward_pool(self):
        self.reward_pool = []
        self.reward_pool.extend(['memory_crystal'] * 8)
        self.reward_pool.extend(['blueprint'] * 8)
        self.reward_pool.extend(['life_support'] * 12)
        self.reward_pool.extend(['jump_drive'] * 12)
        self.reward_pool.extend(['level_fighter'] * 2)
        self.reward_pool.extend(['level_interceptor'] * 2)
        self.reward_pool.extend(['level_bomber'] * 2)
        self.reward_pool.extend(['level_battleship'] * 2)
        random.shuffle(self.reward_pool)

    def new_galaxy(self, row, from_links, level):
        mods = []
        if row == 4:
            mods = [random.choice(["warp_drive", "big_planet", "ship_shield_far_from_home", "atomic_bomb"])]

        if row == 8:
            mods = [random.choice(["battleship"])]

        return {
            'node_type':'galaxy',
            'alien': random.choice(['alien1', 'alien2', 'alien3']),
            'rewards': [self.reward_pool.pop()],
            'difficulty': row,
            'level':level,
            'links': from_links,
            'mods': mods
        }

    def new_store(self, row, from_links):
        offerings = []
        offer_types = ['memory', 'blueprint', 'o2', 'levelup']
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
            elif offer_type == 'levelup':
                offering['ship'] = random.choice(['fighter', 'interceptor', 'bomber', 'battleship'])
            offerings.append(offering)

        return {
            'node_type':'store',
            'offerings':offerings,
            'links': from_links
        }


    def generate_run(self):
        self.data = []
        self.generate_reward_pool()

        all_levels = ['belt', 'scatter', 'enemysplit', 'choke', 'neighbors', 'tunnel', 'bases', 'cross']
        l1 = all_levels[::]
        random.shuffle(l1)
        l2 = all_levels[::]
        random.shuffle(l2)
        levels = l1 + l2

        height = 9
        for row in range(height):
            level = levels.pop()
            self.data.append([])
            num_columns = (height // 2) + 1 - abs((height // 2) - row)
            for column in range(num_columns):
                if row == 0:
                    from_links = []
                elif row < (height // 2) + 1:   
                    from_links = []
                    if column > 0: from_links.append(column - 1)
                    if column < num_columns - 1: from_links.append(column)
                else:
                    from_links = [column, column + 1]

                node = self.new_galaxy(row, from_links, level)
                self.data[-1].append(node)

        self.prune_path()
        self.add_stores()
        return self.data

    def prune_path(self):
        def prune_one():
            row = random.randint(2, len(self.data) - 1)
            col = random.randint(0, len(self.data[row]) - 1)
            neighbors = get_neighbors(self.data, (row,col))
            if len(neighbors) > 1:
                n = random.choice(neighbors)
                self.data[n[0]][n[1]]['links'].remove(col)

        #for _ in range(10):
        #    prune_one()

        while len(get_paths(self.data, (0,0))) > 7:
            prune_one()


        row = 0
        col = 0
        while row < len(self.data):
            while col < len(self.data[row]):
                node = self.data[row][col]
                # If we have no incoming paths...
                if len(node['links']) == 0 and row > 0:
                    # Get rid of the neighbors incoming paths...
                    for nrow, ncol in get_neighbors(self.data, (row,col)):
                        neighbor_node = self.data[nrow][ncol]
                        if col in neighbor_node['links']:
                            new_links = []
                            for link in neighbor_node['links']:
                                if link < col:
                                    new_links.append(link)
                                elif link > col:
                                    new_links.append(link)
                            neighbor_node['links'] = new_links
                # Make object links
                node['object_links'] = [self.data[row - 1][c] for c in node['links']]
                # Make sort value
                node['sort_value'] = col
                col += 1
            row += 1
            col = 0

        row = 0
        col = 0
        while row < len(self.data) - 1:
            while col < len(self.data[row]):
                node = self.data[row][col]
                if len(node['links']) == 0 and row > 0:
                    for col2 in range(len(self.data[row + 1])):
                        above_node = self.data[row + 1][col2]
                        new_links = []
                        for link in above_node['links']:
                            if link < col:
                                new_links.append(link)
                            elif link > col:
                                new_links.append(link - 1)
                        above_node['links'] = new_links
                    self.data[row].pop(col)
                else:
                    col += 1
            row += 1
            col = 0

    def add_stores(self):
        def count_stores():
            store_nums = []
            for path in get_paths(self.data, (0,0)):
                stores = 0
                for nr,nc in path:
                    if self.data[nr][nc]['node_type'] == 'store':
                        stores += 1
                store_nums.append(stores)
            return store_nums

        store_row_places = [3, 5, 7]
        random.shuffle(store_row_places)
        for i in range(3):
            iterations = 0
            done = False
            while not done:
                row = store_row_places[-1]
                if iterations > 3:
                    row = 4
                    while row == 4:                    
                        row = random.randint(2, len(self.data) - 2)
                col = random.randint(0, len(self.data[row])-1)
                old_node = self.data[row][col]
                if old_node['node_type'] == 'store':
                    iterations += 1
                    continue
                self.data[row][col] = self.new_store(row, old_node['links'])
                max_stores = max(count_stores())
                if max_stores < 3 or iterations > 10:
                    done = True
                else:
                    iterations += 1
                    done = False
                    self.data[row][col] = old_node
            store_row_places.pop()

                


def get_neighbors(graph, node):
    neighbors = []
    cnrow, cncol = node
    if len(graph) > cnrow + 1:
        for neighborcol,node in enumerate(graph[cnrow + 1]):
            for link in node['links']:
                if link == cncol:
                    neighbors.append((cnrow + 1, neighborcol))
    return neighbors

def get_paths(graph, node):
    paths = []
    my_path = [node]
    done = False
    while not done:
        cnrow, cncol = my_path[-1]
        current_node = graph[cnrow][cncol]

        # Get neighbors
        neighbors = get_neighbors(graph, my_path[-1])

        # Count neighbors...
        # 0 = we're done
        if len(neighbors) == 0:
            paths.append(my_path)
            return paths

        # 1 = no choice to make
        elif len(neighbors) == 1:
            my_path.append(neighbors[0])

        # 2+ = pick first as mine, and call get_paths for the others. attach path so far to returned paths
        else:
            for n in neighbors[1:]:
                other_paths = get_paths(graph, n)
                for other_path in other_paths:
                    full_other_path = my_path[::]
                    full_other_path.extend(other_path)
                    paths.append(full_other_path)
            my_path.append(neighbors[0])

