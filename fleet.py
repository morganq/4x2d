from ships.ship import FLEET_RADIUS
from button import Button
import pygame
from v2 import V2

FLEET_RADIUS = 20

class FleetManager:
    def __init__(self, scene, civ):

        self.scene = scene
        self.civ = civ
        self.current_fleets = []
        self.ship_fleets = {}
        self.fleet_order_buttons = {}

    def update(self, dt):
        self.current_fleets = generate_fleets(self.scene, self.civ)
        self.ship_fleets = {}
        for fleet in self.current_fleets:
            for ship in fleet.ships:
                self.ship_fleets[ship] = fleet
            # record which fleets have buttons by looking at their first ships
            first_ship = fleet.ships[0]
            def onclick(*args):
                self.recall_fleet(fleet)
            if self.civ == self.scene.my_civ:
                if fleet.is_waiting() and first_ship not in self.fleet_order_buttons:
                    # replace with a graphic and a tooltip
                    b = Button(first_ship.pos, 'Recall Fleet', 'small', onclick)
                    self.scene.ui_group.add(b)
                    self.fleet_order_buttons[first_ship] = b
                elif not fleet.is_waiting() and first_ship in self.fleet_order_buttons:
                    self.fleet_order_buttons[first_ship].kill()
                    del self.fleet_order_buttons[first_ship]

                if first_ship in self.fleet_order_buttons:
                    self.fleet_order_buttons[first_ship].pos = first_ship.pos

    def recall_fleet(self, fleet):
        for ship in fleet.ships: 
            ship.set_state('returning')

    def get_ship_fleet(self, ship):
        if ship in self.ship_fleets:
            return self.ship_fleets[ship]
        else:
            return Fleet([ship])

class Fleet:
    def __init__(self, ships):
        self.ships = ships

    def is_waiting(self):
        average_time = sum(s.waiting_time for s in self.ships) / len(self.ships)
        if average_time >= 6:
            return True
        return False

    def debug_render(self, surface):
        average = V2(0,0)
        min_x, min_y = 999,999
        max_x, max_y = 0,0 
        for ship in self.ships:
            average += ship.pos / len(self.ships)
            min_x = min(min_x, ship.pos.x)
            min_y = min(min_y, ship.pos.y)
            max_x = max(max_x, ship.pos.x)
            max_y = max(max_y, ship.pos.y)
        radius = max(max_x - average.x, average.x - min_x, max_y - average.y, average.y - min_y)
        pygame.draw.circle(surface, (255,0,0), average.tuple_int(), radius, 1)

    def __str__(self):
        return ', '.join([str(s.pos.tuple_int()) for s in self.ships])

def generate_fleets(scene, civ):
    fleets = []
    ships = scene.get_civ_ships(civ)
    for ship in ships:
        fleetless = True
        for fleet in fleets:
            for ship2 in fleet.ships:
                delta = ship2.pos-ship.pos
                if delta.sqr_magnitude() < FLEET_RADIUS ** 2:
                    fleet.ships.append(ship)
                    fleetless = False
                    break
        if fleetless:
            fleets.append(Fleet([ship]))
    
    # merge fleets
    i = 0
    while i < len(fleets) - 1:
        f1 = set(fleets[i].ships)
        j = i + 1
        while j < len(fleets):
            f2 = set(fleets[j].ships)
            if len(f1.intersection(f2)) > 0: # overlap means they share ships
                #print([s.debug_id for s in f1],[s.debug_id for s in f2])
                fleets[i].ships = list(f1.union(f2))
                fleets.pop(j)
            else:
                j += 1
        i += 1

    return fleets