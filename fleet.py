import time
from collections import defaultdict
from sys import path

import pygame

import helper
import ships
from aliens import bossmothership
from button import Button
from colors import PICO_DARKGREEN, PICO_GREEN
from rangeindicator import RangeIndicator
from spaceobject import SpaceObject
from v2 import V2

FLEET_RADIUS = 25
SAME_FLEET_RADIUS = 15
PATH_STEPS_PER_FRAME = 20
PATH_STEP_SIZE = 5
NEAR_PATH_DIST = 40

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
        # Generate new fleets for this frame
        t1 = time.time()
        new_fleets = generate_fleets(self.scene, self.civ)
        t2 = time.time()
        for fleet in new_fleets:
            fleet.update_size_info()        
        
        # For path continuity, we want to figure out which old fleets are the same as which new fleets
        new_fleets_by_target = defaultdict(list)
        for fleet in new_fleets:
            new_fleets_by_target[fleet.target].append(fleet)

        if self.current_fleets:
            old_fleets_by_target = defaultdict(list)
            for fleet in self.current_fleets:
                old_fleets_by_target[fleet.target].append(fleet)

            # We can now try to match the fleets
            for target in old_fleets_by_target.keys():
                a = new_fleets_by_target.get(target, [])
                b = old_fleets_by_target[target]
                for new_fleet in a:
                    for old_fleet in b:
                        #print("comparing", new_fleet, old_fleet)
                        if (new_fleet.pos - old_fleet.pos).sqr_magnitude() < SAME_FLEET_RADIUS ** 2:
                            #print("same fleet found!", new_fleet, old_fleet)
                            new_fleet.path = old_fleet.path[::]
                            new_fleet.path_done = old_fleet.path_done
                            break
                    else:
                        pass
                        #print("no matching fleet")
        
        self.current_fleets = new_fleets[::]
        self.ship_fleets = {}
        for fleet in self.current_fleets:
            fleet.update(dt)
            for ship in fleet.ships:
                ship.fleet = fleet
                self.ship_fleets[ship] = fleet           

            # If this is targeting the boss, need to recreate the path every frame
            needs_repath = isinstance(fleet.target, bossmothership.BossMothership)
            # If the fleet is too far from where it's supposed to be, recreate.
            if (fleet.pos - fleet.path[0]).sqr_magnitude() > 10 ** 2:
                needs_repath = True
            
            if needs_repath:
                fleet.path = [fleet.pos]
                fleet.path_done = False
                fleet.develop_path(100)

        t3 = time.time()
        #print(len(self.current_fleets))
        # Take path steps
        incomplete_fleets = [f for f in self.current_fleets if not f.path_done]
        if incomplete_fleets:
            steps_per_fleet = max(int(PATH_STEPS_PER_FRAME / len(incomplete_fleets)), 1)
            for fleet in incomplete_fleets:
                fleet.develop_path(steps_per_fleet)

        t4 = time.time()
        #print("%.1fms / %.1fms / %.1fms" % ((t2-t1) * 1000, (t3-t2) * 1000, (t4-t3) * 1000))


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
            if (point - fleet.pos).sqr_magnitude() < (fleet.radius + 5) ** 2:
                self.recall_fleet(fleet)

    def update_fleet_markers(self, point):
        for m in self.fleet_markers:
            m.kill()

        self.fleet_markers = []
        for fleet in self.current_fleets:
            if (point - fleet.pos).sqr_magnitude() < (fleet.radius + 5) ** 2:
                m = RangeIndicator(fleet.pos, fleet.radius + 3, PICO_DARKGREEN, 2, 2)
                self.scene.ui_group.add(m)
                self.fleet_markers.append(m)

class Fleet:
    def __init__(self, scene, ships, target):
        self.scene = scene
        self.ships = ships
        self.target = target
        self.selectable_object = None
        self.pos, self.radius = self.get_size_info()
        self.path = [self.pos]
        self.path_done = False

    def is_waiting(self):
        min_time = min(s.waiting_time for s in self.ships)
        if min_time >= 25:
            return True
        return False
        
    def mode_state(self):
        states = defaultdict(lambda:0)
        for s in self.ships:
            states[s.state] += 1
        return max([(b,a) for a,b in states.items()])[1]

    def develop_path(self, num_steps):
        if not self.target:
            return
        for i in range(num_steps):
            if (self.path[-1] - self.target.pos).sqr_magnitude() < (PATH_STEP_SIZE * 2) ** 2:
                self.path_done = True
                return
            if self.scene.flowfield.has_field(self.target):
                new_pt = self.scene.flowfield.walk_field(self.path[-1], self.target, PATH_STEP_SIZE)
            else:
                delta = self.target.pos - self.pos
                new_pt = self.path[-1] + delta.normalized() * PATH_STEP_SIZE
            self.path.append(new_pt)


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

    def update_size_info(self):
        self.pos, self.radius = self.get_size_info()

    def update(self, dt):
        self.update_size_info()
        nearest = 99999999999
        path_end = 0
        for i, pt in enumerate(self.path):
            delta = pt - self.pos
            dsq = delta.sqr_magnitude()
            if dsq > NEAR_PATH_DIST ** 2:
                continue
            if dsq > nearest:
                path_end = i - 1
                break
            nearest = dsq
        if path_end > 0 and path_end < len(self.path) - 1:
            self.path = self.path[path_end:]

    def debug_render(self, surface):
        pass
        #pygame.draw.circle(surface, (255,0,0), self.pos.tuple_int(), self.radius, 1)

    def generate_selectable_object(self):
        radius = max(self.radius, 8)
        self.selectable_object = FleetSelectable(self.scene, self.pos, radius, self.ships[0].owning_civ, self)
        self.scene.game_group.add(self.selectable_object)

    def __str__(self):
        return "p %s, r %s, t %s" % (self.pos, self.radius, str(self.target))
        #return ', '.join([str(s.pos.tuple_int()) for s in self.ships])

def generate_fleets(scene, civ):
    ships = scene.get_civ_ships(civ)
    ships_by_target = defaultdict(list)
    for ship in ships:
        ships_by_target[ship.chosen_target].append(ship)
    
    all_clusters = []
    for target, ships in ships_by_target.items():
        all_clusters.extend(get_clusters(scene, ships))

    return all_clusters


def get_clusters(scene, ships):
    fleets = []
    
    for ship in ships:
        fleetless = True
        for fleet in fleets:
            for ship2 in fleet.ships:
                delta = ship2.pos-ship.pos
                if delta.sqr_magnitude() < FLEET_RADIUS ** 2 and ship.chosen_target == ship2.chosen_target:
                    fleet.ships.append(ship)
                    #fleet.update_size_info()
                    fleetless = False
                    break
        if fleetless:
            f = Fleet(scene, [ship], ship.chosen_target)
            fleets.append(f)
    
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
                #fleets[i].update_size_info()
                fleets.pop(j)
            else:
                j += 1
        i += 1

    return fleets
