from collections import defaultdict

import pygame

import helper
import ships
from button import Button
from colors import PICO_DARKGREEN, PICO_GREEN
from rangeindicator import RangeIndicator
from spaceobject import SpaceObject
from v2 import V2

FLEET_RADIUS = 30

class FleetSelectable(SpaceObject):
    def __init__(self, scene, pos, radius, owning_civ, fleet):
        super().__init__(scene, pos)
        self.layer = -1
        self.selectable = True
        self.radius = radius
        self.collision_radius = radius
        self.owning_civ = owning_civ
        self.fleet = fleet

        self._generate_image()

    def get_selection_info(self):
        return {'type':'fleet'}

    def _generate_image(self):
        self._width = self.radius * 2 + 8
        self._height = self.radius * 2 + 8
        center = V2(self.radius + 4, self.radius + 4)
        self.image = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, PICO_DARKGREEN, center.tuple(), self.radius, 0)
        self._recalc_rect()

class FleetManager:
    def __init__(self, scene, civ):
        self.scene = scene
        self.civ = civ
        self.current_fleets = []
        self.ship_fleets = {}
        self.fleet_order_buttons = {}
        self.fleet_markers = []

    def generate_selectable_objects(self):
        for fleet in self.current_fleets:
            fleet.generate_selectable_object()

    def destroy_selectable_objects(self):
        for fleet in self.current_fleets:
            fleet.selectable_object.kill()
            fleet.selectable_object = None

    def update(self, dt):
        self.current_fleets = generate_fleets(self.scene, self.civ)
        self.ship_fleets = {}
        for fleet in self.current_fleets:
            for ship in fleet.ships:
                ship.fleet = fleet
                self.ship_fleets[ship] = fleet        
        #self.update_fleet_buttons()

    def update_fleet_buttons(self):
        for fleet in self.current_fleets:

            # record which fleets have buttons by looking at their first ships
            first_ship = fleet.ships[0]
            def make_onclick(fleet):
                def onclick(*args):
                    self.recall_fleet(fleet)
                return onclick
            if self.civ == self.scene.my_civ:
                if fleet.is_waiting() and first_ship not in self.fleet_order_buttons:
                    # replace with a graphic and a tooltip
                    b = Button(first_ship.pos, '', 'small', make_onclick(fleet), image_path="assets/recall.png")
                    b.offset = (-0.15, 1.25)
                    self.scene.ui_group.add(b)
                    self.fleet_order_buttons[first_ship] = b
                elif not fleet.is_waiting() and first_ship in self.fleet_order_buttons:
                    self.fleet_order_buttons[first_ship].kill()
                    del self.fleet_order_buttons[first_ship]

                if first_ship in self.fleet_order_buttons:
                    self.fleet_order_buttons[first_ship].pos = first_ship.pos        

    def recall_fleet(self, fleet):
        nearest, dist = helper.get_nearest(fleet.ships[0].pos, self.scene.get_civ_planets(fleet.ships[0].owning_civ))
        if nearest:        
            for ship in fleet.ships: 
                ship.set_target(nearest)
                ship.set_state('returning')

    def get_ship_fleet(self, ship):
        if ship in self.ship_fleets:
            return self.ship_fleets[ship]
        else:
            return Fleet([ship])

    def point_recall(self, point):
        for fleet in self.current_fleets:
            p, r = fleet.get_size_info()
            if (point - p).sqr_magnitude() < (r + 5) ** 2:
                self.recall_fleet(fleet)

    def update_fleet_markers(self, point):
        for m in self.fleet_markers:
            m.kill()

        self.fleet_markers = []
        for fleet in self.current_fleets:
            p, r = fleet.get_size_info()
            if (point - p).sqr_magnitude() < (r + 5) ** 2:
                m = RangeIndicator(p, r + 3, PICO_DARKGREEN, 2, 2)
                self.scene.ui_group.add(m)
                self.fleet_markers.append(m)

class Fleet:
    def __init__(self, ships):
        self.ships = ships
        self.selectable_object = None

    def is_waiting(self):
        average_time = sum(s.waiting_time for s in self.ships) / len(self.ships)
        if average_time >= 6:
            return True
        return False

    def mode_state(self):
        states = defaultdict(lambda:0)
        for s in self.ships:
            states[s.state] += 1
        return max([(b,a) for a,b in states.items()])[1]

    def get_size_info(self):
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
        radius = max(radius, 5)
        return (average, radius)

    def debug_render(self, surface):
        average, radius = self.get_size_info()
        pygame.draw.circle(surface, (255,0,0), average.tuple_int(), radius, 1)

    def generate_selectable_object(self):
        average, radius = self.get_size_info()
        radius = max(radius, 8)
        scene = self.ships[0].scene
        self.selectable_object = FleetSelectable(scene, average, radius, self.ships[0].owning_civ, self)
        scene.game_group.add(self.selectable_object)
        print(self.selectable_object.pos, radius)
        

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
                if delta.sqr_magnitude() < FLEET_RADIUS ** 2 and ship.chosen_target == ship2.chosen_target:
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
