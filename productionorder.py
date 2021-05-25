class ProductionOrder:
    def __init__(self, ship_type, number, period):
        self.ship_type = ship_type
        self.number = number
        self.made = 0
        self.period = period
        self.time = 0
        self.done = False

    def update(self, planet, dt):
        self.time += dt
        if self.number == 0:
            self.done = True
            return
        next_prod_time = self.period / self.number
        if self.time > next_prod_time:
            self.time -= next_prod_time
            planet.add_ship(self.ship_type)
            self.made += 1
            if self.made >= self.number:
                self.done = True