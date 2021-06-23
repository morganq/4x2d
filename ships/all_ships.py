SHIPS_BY_NAME = {
}

def register_ship(ship_class):
    SHIPS_BY_NAME[ship_class.SHIP_NAME] = ship_class
    return ship_class