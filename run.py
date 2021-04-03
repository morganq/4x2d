class RunInfo:
    def __init__(self, data = None):
        self.data = data or self.generate_run()
        self.path = [(0,0)]

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
                    'alien': 'basic',
                    'rewards': ['memory_crystal'],
                    'difficulty': row,
                    'links': from_links
                } 
                self.data[-1].append(galaxy)
        return self.data                