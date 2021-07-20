from aliens import alien
from aliens.alien1 import Alien1


class TutorialAlien(Alien1):
    def set_difficulty(self, difficulty):
        self.difficulty = difficulty
        self.civ.base_stats['mining_rate'] = -1

        self.build_order = buildorder.BuildOrder(self.get_build_order_steps())

alien.ALIENS['tutorial'] = TutorialAlien
