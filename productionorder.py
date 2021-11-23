class ProductionOrder:
    def __init__(self, ship_type, number, period):
        self.ship_type = ship_type
        self.number = number
        self.made = 0
        self.period = period
        self.time = 0
        self.done = False
        self.number_mul = 1

    def update(self, planet, dt):
        self.time += dt * self.number_mul
        if self.number == 0:
            self.done = True
            return
        next_prod_time = self.period / self.number
        if self.time > next_prod_time:
            self.time -= next_prod_time
            planet.add_ship(self.ship_type)
            planet.last_production = self.ship_type
            self.made += 1
            if self.made >= self.number * self.number_mul:
                self.done = True


class PermanentHangarProductionOrder(ProductionOrder):
    def __init__(self, ship_type, time):
        super().__init__(ship_type, 1, time)

    def update(self, planet, dt):
        self.time += dt * self.number_mul
        if self.time > self.period:
            self.time -= self.period
            ship_type = self.ship_type
            #for b in planet.buildings:
            #    if b['building'].upgrade.name == "b_hangar2a" and ship_type not in ['battleship', 'bomber']:
            #        ship_type = "interceptor"
            #    elif b['building'].upgrade.name == "b_hangar2b" and ship_type not in ['battleship']:
            #        ship_type = "bomber"                    
            #    elif b['building'].upgrade.name == "b_hangar3":
            #        ship_type = "battleship"
            planet.add_ship(ship_type)
