from productionorder import ProductionOrder

UPGRADES = {
    'iron':{'building':['econ'], 'production':['fighters'], 'tech':['bullets']}
}

class Upgrade:
    name = ""
    title = "Not Implemented"
    cursor = None
    def apply(self, to):
        pass


UPGRADE_CLASSES = {}

def upgrade(cls):
    UPGRADE_CLASSES[cls.name] = cls
    return cls

@upgrade
class EconUpgrade(Upgrade):
    name = "econ"
    title = "+15% Mining Rate"
    cursor = "allied_planet"

    def apply(self, to):
        to.upgrade_stats['mining_rate'] += 0.25
        # Building

@upgrade
class FightersUpgrade(Upgrade):
    name = "fighters"
    title = "10 Fighters Over 60 seconds"
    cursor = "allied_planet"

    def apply(self, to):
        p = ProductionOrder("fighter", 10, 60)
        to.production.append(p)

@upgrade
class BulletsUpgrade(Upgrade):
    name = "bullets"
    title = "+25% Rate of Fire"

    def apply(self, to):
        to.upgrade_stats['fire_rate'] += 0.25