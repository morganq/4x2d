import random
from math import radians

import game
from upgrade.upgrades import UPGRADE_CLASSES

RUN_INFO_SERIALIZE_FIELDS = [
    'data', 'path', 'saved_technologies', 'blueprints',
    'bonus_population', 'bonus_fighters', 'bonus_supply', 'rerolls', 'o2', 'credits',
    'bonus_credits', 'ship_levels', 'score', 'time_taken', 'ships_lost',
    'reward_list', 'sectors_cleared', 'victory', 'started', 'run_challenges', 'run_modifiers',
    'upgrades_by_sector', 'anticheat_level_started', 'no_score'
]

LEVEL_TITLES = {
    0: {'name':'This is a bug', 'description':'This is a bug'},
    1: {'name':'Surprise Attack', 'description':'We\'ve entered the system undetected - a promising start to our mission.'},
    2: {'name':'Alert!', 'description':'They\'ve issued an alert to the federation. Let\'s make quick work of this before reinforcements are prepared.'},
    3: {'name':'Reinforcements', 'description':'Bad luck, now the whole sector knows we\'re here!'},
    4: {'name':'All In', 'description':'All the alien civs have closed ranks. Nowhere to go but forward.'},
    5: {'name':'Breakthrough', 'description':'We are nearing the Inner Ring of the galaxy, but these aliens guarding it have some kind of advanced technology.'},
    6: {'name':'Discovery', 'description':'We\'re detecting a temporal anomoly on one of these planets - it\'s locked in a time loop!'},
    7: {'name':'Stronghold', 'description':'The signal is not far off. But the enemy\'s defenses are only getting stronger.'},
    8: {'name':'Shop', 'description':'Shop level'},
    9: {'name':'Signal Source', 'description':'This is where the signal originated. There, our comrades, frozen in time! We have to save them!'},
}

# MODIFIERS
FRAGILE_PLANETS = "fragile_planets"
LOW_RANGE = "low_range"
WORKER_LOSS = "worker_loss"
LOW_OXYGEN = "low_oxygen"
SMALL_ARMY = "small_army"
TERRAFORM = 'terraform'
HACKING = 'hacking'
VOID = 'void'
TIMELOOP = 'timeloop'

class RunInfo:
    def __init__(self, data = None):
        self.data = data or self.generate_run()
        self.path = [(0,0)]
        self.saved_technologies = [] # ['t_atomic1']
        self.blueprints = [] # ['b_launchpad1', 'b_launchpad2a', 'b_launchpad3']
        self.bonus_population = 0
        self.bonus_fighters = 0
        self.bonus_supply = 0
        self.rerolls = 3
        self.o2 = 60 * 60 * 1 # 1 hr
        self.credits = 20
        self.bonus_credits = 0
        self.ship_levels = {'fighter':1, 'scout':1, 'interceptor':1, 'bomber':1, 'battleship': 1}
        self.score = 0
        self.sectors_cleared = 0
        self.time_taken = 0
        self.ships_lost = 0
        self.victory = False
        self.reward_list = [] #[{'name':'blueprint'}]
        self.next_path_segment = (0,0)
        self.started = False
        self.run_challenges = [] # Negative mods
        self.run_modifiers = [] # Positive mods
        self.no_score = False # If we restarted or cheated, no score.

        self.upgrades_by_sector = {}

        self.anticheat_level_started = False

    def begin_run(self):
        # challenges
        if LOW_OXYGEN in self.run_challenges:
            self.o2 = 60 * 60 * 0.5

    def complete_sector(self, upgrades):
        current_sector = len(self.path) + 1
        self.upgrades_by_sector[current_sector] = upgrades[::]
        self.anticheat_level_started = False

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
        r.path = [tuple(s) for s in r.path]
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
        self.reward_pool.extend(['o2'] * 5)
        self.reward_pool.extend(['memory_crystal'] * 8)
        self.reward_pool.extend(['blueprint'] * 8)
        self.reward_pool.extend(['life_support'] * 5)
        self.reward_pool.extend(['jump_drive'] * 8)
        self.reward_pool.extend(['level_fighter'] * 2)
        self.reward_pool.extend(['level_interceptor'] * 2)
        self.reward_pool.extend(['level_bomber'] * 2)
        self.reward_pool.extend(['level_battleship'] * 2)
        random.shuffle(self.reward_pool)

    def new_galaxy(self, row, from_links, level, alien):
        signal = None
        mods = []

        rewards = [self.reward_pool.pop()]
        if row == 7:
            rewards.append(self.reward_pool.pop())

        if row == 5:
            mods = [random.choice(["warp_drive", "big_planet", "ship_shield_far_from_home", "atomic_bomb"])]
            signal = "future_tech"

        if row == 9:
            mods = []
            signal = "boss"
            rewards = []

        return {
            'sector':row,
            'node_type':'galaxy',
            'alien': alien,
            'rewards': rewards,
            'difficulty': row,
            'level':level,
            'links': from_links,
            'mods': mods,
            'signal': signal,
            'name':LEVEL_TITLES[row]['name'],
            'description':LEVEL_TITLES[row]['description']
        }

    def new_store(self, row, from_links):
        offerings = []
        offer_types = ['memory_crystal', 'blueprint', 'levelup']
        random.shuffle(offer_types)
        offer_types.insert(2, 'o2')
        for i in range(3):
            offer_type = offer_types.pop()
            offering = {'offer_type':offer_type}
            if offer_type == 'o2':
                offering['quantity'] = 60 * 15
            elif offer_type == 'memory_crystal':
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
            'sector':row,
            'node_type':'store',
            'offerings':offerings,
            'links': from_links
        }


    def generate_run(self):
        highest_avg_cols = 0
        best_run = None
        for i in range(10):
            data = self._generate_run()
            max_cols = max([len(r) for r in data])
            if max_cols != 4:
                continue
            avg_cols = sum([len(r) for r in data]) / len(data)
            if avg_cols > highest_avg_cols:
                best_run = data
                highest_avg_cols = avg_cols
            #if avg_cols < 3:
            #    continue
            #if avg_cols > 3:
            #    continue
            #break
            
        return best_run

    def _generate_run(self):
        self.data = []
        self.generate_reward_pool()

        aliens = ['alien1', 'alien3', 'alien2']
        if game.Game.inst.save.victories > 0:
            random.shuffle(aliens)

        all_levels = ['belt', 'slash', 'orbs', 'enemysplit', 'choke', 'neighbors', 'tunnel', 'bases', 'cross']
        #all_levels = ['orbs'] * 10
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

                if row in [0, 1, 2]:
                    alien = aliens[0]
                elif row in [3, 4]:
                    alien = aliens[1]
                elif row in [5, 6]:
                    alien = aliens[2]
                else:
                    alien = random.choice(aliens)
                node = self.new_galaxy(row, from_links, level, alien)
                self.data[-1].append(node)

        # Signal at the end
        node = self.new_galaxy(height, [0], "boss2", "boss")
        self.data.append([node])

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

        while len(get_paths(self.data, (0,0))) > 35:
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
        row1 = random.choice([3,4])
        rows = [row1, 8]
        for row in rows:
            for col in range(len(self.data[row])):
                old_node = self.data[row][col]
                self.data[row][col] = self.new_store(row, old_node['links'])
        return

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

